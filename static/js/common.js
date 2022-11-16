function getToken(){
    var token = '';
    //todo replace user hardcode
    $.ajax({
       url: getLocalURL() + '/auth/token/',
       type: 'post',
       data: {username:'noelia', password: 'test123456'},
       async: false,
       success: function (data) {
           token = data.access_token;
       },
       error: function (error) {

       }
    });
    return token;
}

function getLocalURL(){
    return window.location.protocol + "//" + window.location.host;
}

function getApiResults(uri){
    var token = getToken();
    var results = {};
    console.log(getLocalURL());
    $.ajax({
       url: getLocalURL() + '/api' + uri,
       method: 'GET',
       contentType: 'application/json',
       async: false,
       headers: {
          'Authorization': 'Bearer ' + token
       },
       success: function (data) {
            results = data;
       },
       error: function (error) {
            console.dir(error);
       }
    });
    return results;
}

function postToApi(uri, bodyParams){
    var token = getToken();
    var results = {};
    $.ajax({
       url: getLocalURL() + '/api' + uri,
       method: 'post',
       data: bodyParams,
       dataType:'json',
       contentType: 'application/json',
       async: false,
       headers: {
          'Authorization': 'Bearer ' + token
       },
       success: function (data) {
            results = data;
       },
       error: function (error) {
            console.dir(error);
       }
    });
    return results;
}

function putToApi(uri, bodyParams){
    var token = getToken();
    var results = {};
    $.ajax({
       url: getLocalURL() + '/api' + uri,
       method: 'put',
       data: bodyParams,
       dataType:'json',
       contentType: 'application/json',
       async: false,
       headers: {
          'Authorization': 'Bearer ' + token
       },
       success: function (data) {
            results = data;
       },
       error: function (error) {
            console.dir(error);
       }
    });
    return results;
}
