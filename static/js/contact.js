function refresh(uid, tweet) {
    var _uuid = uuid();
    msg_channel('POST', '/message/' + uid, {'tweet': tweet, '_message': _uuid}, function (s_msg) {
        insert_before(tweet, _uuid);
    }, function (XMLHttpRequest, textStatus, errorThrown) {
        alert(errorThrown);
    });
}

function insert_before(msg, _uuid) {
    var remove = '<div class="row" id=' + _uuid + '>';
    var value = '<div class="large-11 columns"><div class="panel callout radius">' + msg + '</div></div>';
    var dd = '<div class="large-1 columns"><a href="#" class="' + _uuid + '">X</a></div></div>'
    $("#content").prepend(remove + value + dd);
    $('a').click(function () {
        delete_msg($(this).attr('class'));
    });
}

function msg_all(uid) {
    msg_channel('GET', '/message/' + uid, null, function (all) {
        var html = '';
        var json = JSON.parse(all);
        $(json.data).each(function (index, item) {
            var remove = '<div class="row" id=' + item._message + '>';
            var value = '<div class="large-11 columns"><div class="panel callout radius">' + item.tweet + '</div></div>';
            var dd = '<div class="large-1 columns"><a href="#" class="' + item._message + '">X</a></div></div>'
            html += remove + value + dd;
        });
        $("#content").html(html);
        $('a').click(function () {
            delete_msg($(this).attr('class'));
        });
    }, function (XMLHttpRequest, textStatus, errorThrown) {
        alert(errorThrown);
    });
}

function delete_msg(msg_id) {
    if (!is_uuid(msg_id)) {
        return;
    }
    msg_channel('DELETE', '/message/' + msg_id, null, function (all) {
        $('#' + msg_id).empty();
    }, function (XMLHttpRequest, textStatus, errorThrown) {
        alert(errorThrown);
    });
}

function msg_channel(method, url, stream, okhandler, errhandler) {
    $.ajax({
        method: method,
        url: url,
        data: stream,
        success: okhandler,
        error: errhandler
    });
}

function log_out() {
    msg_channel('DELETE', '/logout', null, function (msg) {
        $(location).attr('href', '/login');
    });
}

function uuid() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : r & 0x3 | 0x8;
        return v.toString(16);
    });
}

function is_uuid(str) {
    //regx can not ok?
    var default_size = [8, 4, 4, 4, 12];
    var arr = str.split("-");
    if (arr.length != 5) {
        return false;
    }
    return true;
}

function close_flash(){
    $('.close').click(function(){
        $(this).parent().remove();
    });
}