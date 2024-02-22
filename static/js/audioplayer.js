
function read(book_id, page, sentence_idx=0) {
	console.log("book_id: "+book_id+" page: "+ page + " idx: "+sentence_idx)
	// HTML5 audio player + playlist controls
	var jsPlayer = document.getElementById('player');

	playlistPerPage = 'playlist-'+page

	if (jsPlayer) {
		// console.log("player"+jsPlayer);

		jsPlayer = {
			wrap: jsPlayer,
			player: (jsPlayer.querySelector('#audio') || { play: function(){}, pause: function(){} }),
			play: (jsPlayer.querySelector('#play') || {}),
			pause: (jsPlayer.querySelector('#pause') || {}),
			repeat: (jsPlayer.querySelector('#repeat') || {}),
			// seek: (jsPlayer.querySelector('.seek') || {}),
			prev: (jsPlayer.querySelector('#prev') || {}),
			next: (jsPlayer.querySelector('#next') || {}),

			// button: (jsPlayer.querySelector('.button') || { style: {} }),
			// wrapList: (jsPlayer.querySelector('#playlist-wrap') || {}),
			wrapList: (document.getElementById(playlistPerPage) || {}),
			action: (jsPlayer.querySelector('#action') || {}),
			// add a page trackerw
			// from_page: (jsPlayer.querySelector('#from_page') || {}),
			from_book: book_id,
			from_page: page,
			autoplay: jsPlayer.querySelector("#autoplay").checked,
			trackCount: 0,
	    	seeking: null,
			playing: false,
			tracks: [],
			track: [],
			idx: sentence_idx
		};

		jsPlayer.playClicked = function jsPlayerPlayClicked(){
			// console.log("jsPlayerPlayClicked "+jsPlayer.idx)
			// console.log("play "+jsPlayer.play)
			// console.log(jsPlayer.wrapList)
			// jsPlayer.loadPlaylist();

			// console.log(jsPlayer.track)

			// jsPlayer.button.style.visibility = 'hidden';
			jsPlayer.pause.style.display = 'block';
			jsPlayer.play.style.display = 'none';
			jsPlayer.playing = true;
			jsPlayer.action.innerHTML = 'Page: ' + jsPlayer.from_page;
			jsPlayer.highlightText(jsPlayer.from_page, jsPlayer.idx)

			// jsPlayer.loadTrack(jsPlayer.idx);

			jsPlayer.player.play();
			// jsPlayer.updateSeek();

		};
		jsPlayer.pauseClicked = function jsPlayerPauseClicked(){
			// console.log("Click pause")
			jsPlayer.play.style.display = 'block';
			jsPlayer.pause.style.display = 'none';
			clearTimeout(jsPlayer.seeking);
			jsPlayer.playing = false;
			jsPlayer.action.innerHTML = 'Page: ' + jsPlayer.from_page;
			jsPlayer.player.pause();
		};
		jsPlayer.loadPlaylist = function jsPlayerLoadPlaylist(){
			console.log("jsPlayerLoadPlaylist -> wrapList " + jsPlayer.wrapList)
			jsPlayer.playlist = jsPlayer.wrapList? jsPlayer.wrapList.querySelectorAll('li') : [];
			console.log("jsPlayerLoadPlaylist -> li elems" + jsPlayer.wrapList.querySelectorAll('li'))

			console.log(jsPlayer.playlist)

			var len = jsPlayer.playlist.length,
				tmp, i;
			for (i = 0; i < len; i++) {
				jsPlayer.playlist[i].dataset = {};
				tmp = jsPlayer.playlist[i].querySelector('a');


				jsPlayer.playlist[i].dataset.idx = i + 1;
				jsPlayer.trackCount++;
				jsPlayer.tracks.push({
					"file": tmp.href,
					"name": (tmp.textContent || tmp.innerText).replace(/^\\s+|\\s+$/g, ''),
					"track": i + 1
				});
			}
		};
		jsPlayer.loadTrack = function jsPlayerLoadTrack(idx){
			var len = jsPlayer.playlist.length,
				i;
			for (i=0; i < len; i++) {
				if (jsPlayer.playlist[i].classList) {
					if (i === idx) {
						jsPlayer.playlist[i].classList.add('sel');
					} else {
						jsPlayer.playlist[i].classList.remove('sel');
					}
				}
			}
			// jsPlayer.title.innerHTML = jsPlayer.tracks[idx].name;
			jsPlayer.player.src = jsPlayer.tracks[idx].file;

		};
		jsPlayer.playTrack = function jsPlayerPlayTrack(idx){
			// console.log("playTrack: "+ idx)
			// console.log("tracks: "+ jsPlayer.tracks + " length " + jsPlayer.tracks.length)

			if (idx == 1){
				book_id = jsPlayer.from_book
				page_num = jsPlayer.from_page
				jsPlayer.preload(book_id, page_num)
			}
			jsPlayer.loadTrack(idx);
			jsPlayer.playing = true;
			jsPlayer.playClicked();

		};
		jsPlayer.highlightText = function Text(page_num, idx) {
			// console.log("reach highlightText ");
			// console.log("page_num "+page_num);

			page = document.getElementById("page-text-"+page_num)
			// console.log(page);

			sentences = page.getElementsByClassName("book-sentence");
			// sentences = document.getElementsByClassName("book-sentence");
			// console.log(sentences);

			for (var i = sentences.length - 1; i >= 0; i--) {
				if (i == idx){
					sentences[i].setAttribute("style", "background-color: rgb(252 211 77);")  //bg-amber-300

				}
				else {
					sentences[i].setAttribute("style", "")

				}
			}
			// console.log(sentences);
		}
		jsPlayer.preload = async function jsPlayerPreload(book_id, page_num){
			preload_url = "/read_page?book_id="+book_id+"&page_num="+page_num
			console.log(preload_url)

			fetch(preload_url)

		}
		jsPlayer.init = function jsPlayerInit(){
			var track = (jsPlayer.wrap && jsPlayer.wrap.dataset && jsPlayer.wrap.dataset.url)? jsPlayer.wrap : null,
				tmp, i;
			if (!!document.createElement('audio').canPlayType('audio/wav')) {
				if (jsPlayer.wrapList && jsPlayer.wrapList.querySelectorAll('ol > li').length > 0) {
					jsPlayer.loadPlaylist();
				} else if (track) {
					jsPlayer.tracks = [{
						"file": track.dataset.url,
						"name": (track.dataset.title || ''),
						"track": 1
					}];
				}
				if (jsPlayer.tracks.length > 0) {
					// console.log(jsPlayer.player)
					// console.log(jsPlayer.tracks)
					if (jsPlayer.player) {
						jsPlayer.player.addEventListener('ended', function playerEnded(){
							if (jsPlayer.idx + 1 < jsPlayer.trackCount) {
								jsPlayer.idx++;
								jsPlayer.playTrack(jsPlayer.idx);
							} else {
								jsPlayer.action.innerHTML = 'Page end.';
								//todo: preload and play next page
								jsPlayer.player.pause();

								next_page = document.getElementById("page-"+(jsPlayer.from_page +1))

								if (next_page && jsPlayer.autoplay){
									console.log("Reading the next page");

									read(jsPlayer.from_book, jsPlayer.from_page+1,0)
								}
								else{
									console.log("End of stream");
									jsPlayer.idx = 0;
									jsPlayer.loadTrack(jsPlayer.idx);

								}
							}
						}, true);
						jsPlayer.player.addEventListener('loadeddata', function playerLoadeddata(){
							// jsPlayer.setDuration();
						}, true);
					};


					if (jsPlayer.play) {
						jsPlayer.play.addEventListener('click', jsPlayer.playClicked, true);
					}
					if (jsPlayer.pause) {
						jsPlayer.pause.addEventListener('click', jsPlayer.pauseClicked, true);
					}
					if (jsPlayer.repeat) {
						jsPlayer.repeat.addEventListener('click', function buttonClicked(event){
							event.preventDefault();
							jsPlayer.loadTrack(jsPlayer.idx);
							jsPlayer.highlightText(jsPlayer.from_page, jsPlayer.idx)

							jsPlayer.playClicked();
						}, true);
					}
					if (jsPlayer.prev) {
						jsPlayer.prev.addEventListener('click', function prevClicked(event){
							event.preventDefault();
							if (jsPlayer.idx - 1 > -1) {
								jsPlayer.idx--;
								jsPlayer.loadTrack(jsPlayer.idx);
								jsPlayer.highlightText(jsPlayer.from_page, jsPlayer.idx)

								if (jsPlayer.playing) {
									jsPlayer.action.innerHTML = 'Now Playing&hellip;';

									jsPlayer.player.play();
								}
							} else {
								jsPlayer.action.innerHTML = 'Paused&hellip;';
								jsPlayer.playing = false;
								jsPlayer.player.pause();
								jsPlayer.idx = 0;
								jsPlayer.loadTrack(jsPlayer.idx);
							}
						}, true);
					}
					if (jsPlayer.next) {
						jsPlayer.next.addEventListener('click', function nextClicked(event){
							event.preventDefault();
							if (jsPlayer.idx + 1 < jsPlayer.trackCount) {
								jsPlayer.idx++;
								jsPlayer.loadTrack(jsPlayer.idx);
								jsPlayer.highlightText(jsPlayer.from_page, jsPlayer.idx)
								if (jsPlayer.playing) {
									jsPlayer.action.innerHTML = 'Now Playing&hellip;';
									jsPlayer.player.play();

								}
							} else {
								jsPlayer.action.innerHTML = 'Paused&hellip;';
								jsPlayer.playing = false;
								jsPlayer.player.pause();
								jsPlayer.idx = 0;
								jsPlayer.loadTrack(jsPlayer.idx);
							}
						}, true);
					}
					if (jsPlayer.wrapList) {
						jsPlayer.wrapList.addEventListener('click', function listClicked(event){
							var parent = event.target.parentNode;
							if (parent.parentNode.tagName.toLowerCase() === 'ol') {
								event.preventDefault();
								var len = jsPlayer.playlist.length,
								i;
								for (i = 0; i < len; i++) {
									if (parent.dataset.idx == i + 1) {
										jsPlayer.idx = i;
										jsPlayer.playTrack(jsPlayer.idx);
										i = len;
									}
								}
							}
						}, true);
					}

				}
			}
			if (jsPlayer.tracks.length > 0) {
				jsPlayer.wrap.className += ' enabled';
				jsPlayer.loadTrack(jsPlayer.idx);
			}
		};
		jsPlayer.init();
		// jsPlayer.playTrack(jsPlayer.idx)
		jsPlayer.playClicked()
	}

}

