var apigClient;
apigClient = apigClientFactory.newClient({
	region: 'us-east-1'
});

function chatbotResponse() {
		
		// User's own message for display
		lastUserMessage = userMessage();

		return new Promise(function (resolve, reject) {
			talking = true;
			let params = {};
			let additionalParams = {
				headers: {
				"x-api-key" : 'YOUR API KEY HERE'
				}
			};
			var body = {
			"message" : lastUserMessage
			}
			apigClient.chatbotPost(params, body, additionalParams)
			.then(function(result){
				
				reply = result.data.body.slice(1, -1);
							
				$("<li class='replies'><img src='' alt='' /><p>" + reply + "</p></li>").appendTo($('.messages ul'));
				$('.message-input input').val(null);
				$('.contact.active .preview').html('<span>You: </span>' + reply);
				$(".messages").animate({ scrollTop: $(document).height() }, "fast");
				
				resolve(result.data.body);
				botMessage = result.data.body;
			}).catch( function(result){
				// Add error callback code here.
				console.log(result);
				botMessage = "Couldn't connect"
				reject(result);
			});
		})
	}

function userMessage() {

	message = $(".message-input input").val();
	if($.trim(message) == '') {
		return false;
	}

	$('<li class="sent"><img src="" alt="" /><p>' + message + '</p></li>').appendTo($('.messages ul'));
	$('.message-input input').val(null);
	$('.contact.active .preview').html('<span>You: </span>' + message);
	$(".messages").animate({ scrollTop: $(document).height() }, "fast");

	return message;
};

$('.submit').click(function() {
	chatbotResponse();
});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
		chatbotResponse();
    return false;
  }
});