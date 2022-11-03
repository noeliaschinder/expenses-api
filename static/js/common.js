function getToken(){
    var token = '';
    $.ajax({
       url: 'http://127.0.0.1:8000/auth/token/',
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

function getApiResults(uri){
    var token = getToken();
    var results = {};
    $.ajax({
       url: 'http://127.0.0.1:8000/api' + uri,
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
       url: 'http://127.0.0.1:8000/api' + uri,
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
       url: 'http://127.0.0.1:8000/api' + uri,
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
