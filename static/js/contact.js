function refresh(uid, tweet) {
    $.ajax({
        method: 'POST',
        data: {'tweet': tweet},
        url: '/message/' + uid,
        success: function (s_msg) {
            msg_all();
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}

function msg_all() {
    $.ajax({
        method: 'GET',
        url: '/message',
        success: function (all) {
            var html = '';
            JSON.parse(all, function (key, value) {
                if (key == "tweet") {
                    html += '<div class="panel callout radius">' + value + '</div>';
                }
            });
            $("#content").html(html);
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
}