$(document).ready(function () {
    var entity = $('#entity').val();
    var action = $('#action').val();
    var entityId = $('#entityId').val();

    $('.source-ajax-call').each(function(index, elem){
        var sourceEntity = elem['dataset']['entity'];
        var selectedValue = elem['dataset']['value'];
        var results = getApiResults('/' + sourceEntity + '/')['data'];
        $.each(results, function (i, item) {
            $(elem).append($('<option>', {
                value: item.id,
                text : item.label,
                selected : selectedValue == item.id
            }));
        });
    });

    $( "#mainForm" ).submit(function( event ) {
        event.preventDefault();
        var btnClickedId = event.originalEvent.submitter.id;
        if( $( "#mainForm" )[0].checkValidity() ){
            var formInputs = $( this ).serializeArray();
            var postParams = {};
            $.each(formInputs, function( index, item ) {
                if(item.value){
                    postParams[item.name] = item.value;
                }
            });
            var get_params = [];
            $( ".get-param" ).each(function(index,elem){
                if($(elem).val()){
                    get_params.push(elem.name + '=' + $(elem).val());
                }
                delete(postParams[elem.name]);
            })
            var extra_params = '?' + get_params.join('&');
            if(action == 'edit'){
                var results = putToApi('/' + entity + '/' + entityId + extra_params, JSON.stringify(postParams));
            }else{
                var results = postToApi('/' + entity + extra_params, JSON.stringify(postParams));
                entityId = results.id;
            }
            if(entityId > 0){
                if(btnClickedId == 'enviar-y-volver-al-listado'){
                    window.location.href = location.protocol + '//' + location.host + '/' + entity + '/';
                }else if(btnClickedId == 'enviar-y-agregar-nuevo'){
                    window.location.href = location.protocol + '//' + location.host + '/' + entity + '/add/';
                } else {
                    window.location.href = location.protocol + '//' + location.host + '/' + entity + '/edit/' + entityId;
                }
            }
        }
    });

    $('.input-month').each(function(index, elem){
        var originalDate = elem.defaultValue;
        if(originalDate != 'None'){
            var year = originalDate.slice(0,4);
            var month = originalDate.slice(4);
            elem.defaultValue = year + '-' + month;
        }
    });

    $('.input-date').each(function(index, elem){
        var originalDate = elem.defaultValue;
        if(originalDate != 'None'){
            var year = originalDate.slice(0,4);
            var month = originalDate.slice(4,2);
            var day = originalDate.slice(6);
            elem.defaultValue = year + '-' + month + '-' + day;
        }
    });

})


  