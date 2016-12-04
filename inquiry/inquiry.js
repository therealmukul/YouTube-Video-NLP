var i = {}

i.videoId = function() {
   return window.location.search.split('=')[1]
}
//
// i.searchTerm = function() {
//     return document.getElementsByClassName('i-search')[0].value.toLowerCase()
// }
//
i.loadYTPlayer = function() {
   var node = document.getElementsByClassName('watch-secondary-actions')[0]
}


i.getSentiment = function(onLoad) {
   var id = i.videoId()
   console.log(id);
   fetch('https://localhost:8000/sentiment/' + id)
      .then(function(res) {
         res.json().then(function(json) {
            var data = json
            console.log(data);
            for (i = 0; i < data.length; i++) {
               start_time = data[i][0]
               end_time = data[i][1]
               sentiment = data[i][2]

               var videoLength = data[data.length - 1][1]
               var width = document.getElementsByClassName('ytp-progress-list')[0].clientWidth
               var left = Math.floor((start_time / videoLength) * width)
               var right = Math.floor((end_time / videoLength) * width)
               var length = right - left

               var e = document.createElement('div')
               e.setAttribute('class', 'ytp-ad-progress i-marker hint--bottom')
               e.style.width = '' + length + 'px'
               e.style.left = '' + left + 'px'

               if (sentiment > 0.0) {
                  // Positive
                  e.style['backgroundColor'] = 'mediumspringgreen'
               } else if (sentiment < 0.0) {
                  // Negative
                  e.style['backgroundColor'] = '#9000fa'
               } else {
                  // Neutral
                  e.style['backgroundColor'] = '#a7a7a7'
               }

               document.getElementsByClassName('ytp-ad-progress-list')[0].appendChild(e)

            }
         })
      })
}

window.addEventListener("DOMContentLoaded", function() {
   console.log("DONE")
})


i.loadYTPlayer()
i.getSentiment()

//     fetch(`https://backend.inquiry.tech:9000/exists/${i.videoId()}`)
//         .then(function(res) {
//             if (res.status >= 400) {
//                 node.setAttribute('class', 'i-search-icon not-loaded')
//                 document.getElementsByClassName('i-container')[0].onclick = function() {
//                     node.setAttribute('class', 'i-search-icon loading fa-spin')
//                     fetch(`https://backend.inquiry.tech:9000/process/${i.videoId()}`)
//                     document.getElementsByClassName('i-search')[0].setAttribute('class', 'i-search processing')
//
//                     setTimeout(function() {
//                         document.getElementsByClassName('i-container')[0].onclick = function() {}
//                         node.setAttribute('class', 'i-search-icon')
//                         document.getElementsByClassName('i-search')[0].setAttribute('class', 'i-search')
//                         document.getElementsByClassName('i-search')[0].disabled = false
//                     }, 25000)
//                 }
//             } else {
//                 node.setAttribute('class', 'i-search-icon')
//                 document.getElementsByClassName('i-container')[0].onclick = function() {
//                     document.getElementsByClassName('i-search')[0].disabled = false
//                 }
//             }
//
//             //onLoad()
//         })
// }
//
// i.loadYTPlayer = function() {
//     var script = document.createElement('script')
//     script.textContent = `(function() {
//         document.body.setAttribute('ytplayer', JSON.stringify(ytplayer.config.args))
//     })()`
//
//     document.body.appendChild(script);
//     i.ytargs = JSON.parse(document.body.getAttribute('ytplayer'))
// }
//
// i.createMarker = function(time, text) {
//     var videoLength = parseInt(i.ytargs.length_seconds)
//     var width = document.getElementsByClassName('ytp-progress-list')[0].clientWidth
//     var left = Math.floor((time / videoLength) * width)
//
//     var marker = (function() {
//         var e = document.createElement('div')
//         e.setAttribute('class', 'ytp-ad-progress i-marker hint--bottom')
//         e.setAttribute('data-hint', text)
//         e.style.width = '' + Math.max(Math.ceil(width / videoLength), 6) + 'px'
//         e.style.left = '' + left + 'px'
//         e.style['backgroundColor'] = 'mediumspringgreen'
//         return e
//     })()
//
//     document.getElementsByClassName('ytp-ad-progress-list')[0]
//         .appendChild(marker)
// }
//
// i.createSearch = function(onSearch) {
//     var searchBox = (function() {
//         var container = document.createElement('form')
//         container.setAttribute('class', 'i-container')
//
//         var label = document.createElement('label')
//         label.setAttribute('for', 'i-searcher')
//         label.setAttribute('class', 'i-search-icon')
//
//         var input = document.createElement('input')
//         input.setAttribute('type', 'text')
//         input.setAttribute('autocomplete', 'off')
//         input.setAttribute('class', 'i-search')
//         input.setAttribute('name', 'i-searcher')
//         input.disabled = true
//
//         var results = document.createElement('label')
//         results.setAttribute('class', 'i-results')
//
//         var submit = document.createElement('input')
//         submit.setAttribute('type', 'submit')
//         submit.style.display = 'none'
//
//         container.appendChild(label)
//         container.appendChild(input)
//         container.appendChild(results)
//         container.appendChild(submit)
//
//         container.onsubmit = function(e) {
//             e.preventDefault()
//             onSearch()
//         }
//
//         return container
//     })()
//
//     var header = document.getElementById('watch7-user-header')
//     header.appendChild(searchBox)
// }
//
// i.clearMarkers = function() {
//     var elements = document.getElementsByClassName('i-marker')
//     for (var j = 0; j < elements.length; j++) {
//         elements[j].style.display = 'none'
//     }
// }
//
// i.doSearch = function() {
//     i.clearMarkers()
//     fetch(`https://backend.inquiry.tech:9000/query/${i.videoId()}/${i.searchTerm()}`)
//         .then(function(res) {
//             return res.json()
//         }).then(function(times) {
//             times.forEach(function(time) {
//                 i.createMarker(time, i.searchTerm())
//             })
//
//             var results = document.getElementsByClassName('i-results')[0]
//             results.textContent = `${times.length} Results`
//         })
// }
//
// var spinnerTimeout = undefined;
// i.search = function(term) {
//     var node = document.getElementsByClassName('i-search-icon')[0]
//     node.setAttribute('class', 'fa-spin i-search-icon loading')
//
//     if (spinnerTimeout) {
//         clearTimeout(spinnerTimeout)
//     }
//
//     spinnerTimeout = setTimeout(function() {
//         node.setAttribute('class', 'i-search-icon')
//         i.doSearch()
//     }, 500)
// }
//
// i.loadYTPlayer()
// i.createSearch(i.search)
// i.loadVideo()

// document.addEventListener('spfdone' , function() {
//    //  i.clearMarkers()
//    //  i.loadYTPlayer()
//    //  i.createSearch(i.search)
//    //  i.loadVideo()
// })
