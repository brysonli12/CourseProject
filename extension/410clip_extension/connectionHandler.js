const CONNECTION = "http://brysonli.pythonanywhere.com/"

// TODO: change error logging to here instead of individual methods

var HttpClient = function() {
    this.get = function(aUrl, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.onreadystatechange = function() {
            if (anHttpRequest.readyState == 4)// && anHttpRequest.status == 200) {
              aCallback(anHttpRequest); //aHttpRequest.responseText
        }
        anHttpRequest.open( "GET", aUrl, true );
        //anHttpRequest.setRequestHeader('Authorization', window.seeknet_token);
        anHttpRequest.send( null );
    }
    this.post = function(aUrl, data, aCallback) {
        var anHttpRequest = new XMLHttpRequest();
        anHttpRequest.onreadystatechange = function() {
            if (anHttpRequest.readyState == 4)// && anHttpRequest.status == 200) {
              aCallback(anHttpRequest);
        }
        anHttpRequest.open( "POST", aUrl, true );
        //anHttpRequest.setRequestHeader('Authorization', window.seeknet_token);
        anHttpRequest.send( data );
    }
}
var client = new HttpClient();

var copyPasteForm = document.getElementById('copy-paste')


var cs410DLSearchForm = document.getElementById('dl-search')
cs410DLSearchForm.addEventListener('submit', (event) => {
  event.preventDefault();
  var data = new FormData(cs410DLSearchForm);
  if(copyPasteForm.value) {
    data.append("highlighted_text", copyPasteForm.value)
  } else {
    data.append("highlighted_text", window.highlighted_text)
  }
  query = data.get("dl_search_query")

  post_url = CONNECTION + "search"
  client.post(post_url, data, function(response) {
    console.log(response.responseText)//.responseText)
    var parsed_response = JSON.parse(response.responseText)

    if (response.status == 200) {
      var redirectWindow = window.open(parsed_response["redirect_url"], '_blank');
      redirectWindow.location;
    } else {
      alert(response.message)
    }
  })
});


setTimeout(() => console.log("test"), 2000)

var saveContextForm = document.getElementById("save-context")
saveContextForm.addEventListener('submit', (event) => {
  event.preventDefault();
  var data = new FormData(saveContextForm);
  data.append("page_title", window.source_title)
  if(copyPasteForm.value) {
    data.append("highlighted_text", copyPasteForm.value)
  } else {
    data.append("highlighted_text", window.highlighted_text)
  }
  data.append("source_url", window.source_url)

  console.log(data);

  post_url = CONNECTION + "add_doc"
  client.post(post_url, data, function(response){
      console.log(response);
      console.log(response.responseText)
      var parsed_response = JSON.parse(response.responseText);
      alert(parsed_response.message)
  })
});

var highlighted_text = document.getElementById('highlighted-text')
var page_title = document.getElementById("page-title")
var login_div = document.getElementById("login-div")
var content_div = document.getElementById("content-div")

function handleExtensionOpen() {
    chrome.tabs.query({active: true, currentWindow: true},
      (tabs) => {
          var url = tabs[0].url;
          var title = tabs[0].title
          window.source_url = url;
          window.source_title = title;

          chrome.scripting.executeScript(
            {
              target: {tabId: tabs[0].id},
              function: () => getSelection().toString()
            },
            (result) => {
              highlighted_text.innerHTML = "<text><b>Highlighted text</b>: " + escapeHtml(result[0].result) + "</text><br>"
              window.highlighted_text = result[0].result
              page_title.innerHTML = "<text><b>Page Title</b>: " + window.source_title + "</text><br>"

            }
          )

    });
  }

window.addEventListener('load', handleExtensionOpen)

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }
