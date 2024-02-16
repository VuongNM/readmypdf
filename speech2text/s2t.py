import torch
torch.manual_seed(0)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

import random
random.seed(0)

import numpy as np
np.random.seed(0)

import phonemizer as _phonemizer


# load packages
import os
import time
import random
import yaml
from munch import Munch
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
import torchaudio
import librosa
from nltk.tokenize import word_tokenize

from speech2text.models.models import *
from speech2text.utils.utils import *
from speech2text.utils.text_utils import TextCleaner
from speech2text.modules.diffusion.sampler import DiffusionSampler, ADPM2Sampler, KarrasSchedule
from speech2text.utils.PLBERT.util import load_plbert
from scipy.io.wavfile import write

DEVICE = 'cpu'

SAMPLING_RATE = 24000

def length_to_mask(lengths):
    mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
    mask = torch.gt(mask+1, lengths.unsqueeze(1))
    return mask


class Reader(object):
    def __init__(self, *args, **kwargs):
        text_cleaner = TextCleaner()
        phonemizer = _phonemizer.backend.EspeakBackend(language='en-us', preserve_punctuation=True,  with_stress=True)
        model_config = yaml.safe_load(open("speech2text/models/LJSpeech/config.yml"))


        # load pretrained ASR model
        ASR_config = model_config.get('ASR_config', False)
        ASR_path = model_config.get('ASR_path', False)
        text_aligner = load_ASR_models(ASR_path, ASR_config)

        # load pretrained F0 model
        pitch_extractor = load_F0_models(model_config.get('F0_path', False))

        # load BERT model
        plbert = load_plbert(model_config.get('PLBERT_dir', False))

        model = build_model(recursive_munch(model_config['model_params']), text_aligner, pitch_extractor, plbert)
        _ = [model[key].eval() for key in model]
        _ = [model[key].to(DEVICE) for key in model]


        params_whole = torch.load("speech2text/models/LJSpeech/epoch_2nd_00100.pth", map_location=DEVICE)
        params = params_whole['net']

        for key in model:
            if key in params:
                print('%s loaded' % key)
                try:
                    model[key].load_state_dict(params[key])
                except:
                    from collections import OrderedDict
                    state_dict = params[key]
                    new_state_dict = OrderedDict()
                    for k, v in state_dict.items():
                        name = k[7:] # remove `module.`
                        new_state_dict[name] = v
                    model[key].load_state_dict(new_state_dict, strict=False)
        _ = [model[key].eval() for key in model]

        sampler = DiffusionSampler(
            model.diffusion.diffusion,
            sampler=ADPM2Sampler(),
            sigma_schedule=KarrasSchedule(sigma_min=0.0001, sigma_max=3.0, rho=9.0), # empirical parameters
            clamp=False
        )

        self.model = model
        self.sampler = sampler
        self.phonemizer  = phonemizer
        self.text_cleaner  = text_cleaner

    def LFinference(self, text, s_prev, noise, alpha=0.7, diffusion_steps=5, embedding_scale=1):
        text = text.strip()
        text = text.replace('"', '')
        ps = self.phonemizer.phonemize([text])
        ps = word_tokenize(ps[0])
        ps = ' '.join(ps)

        tokens = self.text_cleaner(ps)
        tokens.insert(0, 0)
        tokens = torch.LongTensor(tokens).to(DEVICE).unsqueeze(0)

        model = self.model
        sampler = self.sampler


        with torch.no_grad():
            input_lengths = torch.LongTensor([tokens.shape[-1]]).to(tokens.device)
            text_mask = length_to_mask(input_lengths).to(tokens.device)

            t_en = model.text_encoder(tokens, input_lengths, text_mask)
            bert_dur = model.bert(tokens, attention_mask=(~text_mask).int())
            d_en = model.bert_encoder(bert_dur).transpose(-1, -2)

            s_pred = sampler(noise,
                  embedding=bert_dur[0].unsqueeze(0), num_steps=diffusion_steps,
                  embedding_scale=embedding_scale).squeeze(0)

            if s_prev is not None:
                # convex combination of previous and current style
                s_pred = alpha * s_prev + (1 - alpha) * s_pred

            s = s_pred[:, 128:]
            ref = s_pred[:, :128]

            d = model.predictor.text_encoder(d_en, s, input_lengths, text_mask)

            x, _ = model.predictor.lstm(d)
            duration = model.predictor.duration_proj(x)
            duration = torch.sigmoid(duration).sum(axis=-1)
            pred_dur = torch.round(duration.squeeze()).clamp(min=1)

            pred_aln_trg = torch.zeros(input_lengths, int(pred_dur.sum().data))
            c_frame = 0
            for i in range(pred_aln_trg.size(0)):
                pred_aln_trg[i, c_frame:c_frame + int(pred_dur[i].data)] = 1
                c_frame += int(pred_dur[i].data)

            # encode prosody
            en = (d.transpose(-1, -2) @ pred_aln_trg.unsqueeze(0).to(DEVICE))
            F0_pred, N_pred = model.predictor.F0Ntrain(en, s)
            out = model.decoder((t_en @ pred_aln_trg.unsqueeze(0).to(DEVICE)),
                                    F0_pred, N_pred, ref.squeeze().unsqueeze(0))

        return out.squeeze().cpu().numpy(), s_pred



    def read(self, passage):
        sentences = passage.split('.') # simple split by comma
        wavs = []
        s_prev = None
        for text in sentences:
            if text.strip() == "": continue
            text += '.' # add it back
            noise = torch.randn(1,1,256).to(DEVICE)
            wav, s_prev = self.LFinference(text, s_prev, noise, alpha=0.7, diffusion_steps=10, embedding_scale=1.5)
            wavs.append(wav)
        return np.concatenate(wavs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="The text to be read", type=str)
    parser.add_argument("split_sentence", help="Split text into sentences for better reading", type=bool)
    parser.add_argument("speed", help="The reading speed.", type=float)
    parser.add_argument("output", help="Output sound file location", type=str)

    args = parser.parse_args()

    text = args.text
    split_sentence =  args.split_sentence
    speed =  args.speed

    reader = Reader()

    if split_sentence:
        sound = []
        sentences = nltk.sent_tokenize(text)
        for s in sentences:
            if len(s):
                sound += reader.read(s)
        sound = np.concatenate(sound)
    else:
        sound = reader.read(text)


    # r = Reader()
    # sound = r.read('this is sparta!')
    write(output, SAMPLING_RATE, sound)










