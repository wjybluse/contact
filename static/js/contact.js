function refresh(uid,tweet){
	if(uid==null||typeof uid == 'undefined'||uid.empty())
	{
		return null;
	}
	if(tweet==null||tweet.empty())
	{
		return null;
	}
	$.ajax({
		method:'POST',
		data:{'tweet':tweet},
		url:'/message/'+uid,
		success:function(s_msg){
			alert(s_msg);
		},
		error:function(XMLHttpRequest, textStatus, errorThrown){
			msg_all();
		}
	});
}

function msg_all()
{
	$.ajax({
		method:'GET',
		url:'/message',
		success:function(all){
			var html='';
			for(var message in all){
				html='<div class="panel callout radius">'+message+'</div>';
			}
			$("#content").html(html);
		},
		error:function(XMLHttpRequest, textStatus, errorThrown){
			alert(errorThrown);
		}
	});
}