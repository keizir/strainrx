'use strict';

function validateEmail($email) {
	var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
	return emailReg.test($email);
}

function loadBusinessTypes() {
	$.ajax({
		url: "/api/v1/signup/business-types/",
		type: "GET",
		dataType: "json"
	}).done(function(response) {
		$.map(response, function(obj) {

			$(".business-type").append(
				`<label><input type="radio" name="business_type" class="business_type" data-id="${obj.id}"> ${obj.name}</label>`
			);

			let businessTypeDetails = '';
			$.map(obj.what_you_get, function(el) {
				businessTypeDetails += `<li>${el.name}</li>`

			});

			$(".elements-2").append(
				`<div class="wat-do-you-get business-type-${obj.id}" >
					<h3>What you get:</h3>
					<ul>
						${businessTypeDetails}
					</ul>
					<a  class="more">+more</a>
				</div>`
			);
		});
	});
}

function showPassword() {
    var x = document.getElementById("id_password");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

$(document).ready(function() {
	localStorage.clear();

	$("#next").attr('disabled', 'disabled');

	$.ajax({
		url: "/api/v1/signup/generate-token/",
		type: "GET",
		dataType: "json"
	}).done(function(response) {
		if (!response.error) {
			localStorage.setItem('pftoken', response.pftoken);
			$("#next").attr('disabled', false);
		}
  	});

  	if ($("#form-signup-complete").length > 0) {
		if (localStorage.getItem('user_profile') === null) {
			location.href = "/";
		}
  	}

	// Load business types on page load.
	loadBusinessTypes();

	if($(".flagstrap").length){
		$.flagStrap.set('/static/jquery-flagstrap/dist/css/flagstrap.min.css');
		$(".flagstrap").flagStrap({
			"countries": {
				"CA": "Canada",
				"US": "United States"
			}
		});
	}

	$("body").on("click", "#basic li a", function(e) {
		var dataValue = $(this).attr("data-val");
		$("#basic button").attr("data-val", dataValue);
	});

	$("#next").click(function(e) {

		var failCount1 = 0;
		var failCount2 = 0;
		var failCount3 = 0;

		if (($("#basic button").attr("data-val") == "") ||
			($("#basic button").attr("data-val") == undefined) ||
			($("#basic button").attr("data-val") == null)) {

            $(".dropdown-toggle").addClass("error");
            $(".flag-helper-text").html('Please select your country.');
			failCount3 = 1;

		} else {
            $(".dropdown-toggle").removeClass("error");
            $(".flag-helper-text").html('');
		}

		$(".step-1 input").each(function(e) {
			if ($.trim($(this).val()) === "") {
                $(this).addClass("error");
                if($(this).hasClass('step1-first-name')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter your first name.');
                }
                if($(this).hasClass('step1-last-name')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter your last name.');
                }
                if($(this).hasClass('step1-email')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid email address.');
                }
                if($(this).hasClass('step1-password')) {
                    $(this).parent().find('.signup-helper-text').html('Please create password.');
                }
				failCount2++;
			} else {
				$(this).removeClass("error");
				$(this).parent().find('.signup-helper-text').html('');
			}
		});

		$(".step-1 input:checkbox").each(function() {
			if (!$(this).is(":checked")) {
				$(".checked label").addClass("error");
				failCount3++;
			} else {
				$(this).removeClass("error");
			}
		});

		if (!validateEmail($("#id_email").val())) {
			failCount1++;
			$("#id_email").addClass("error");
		}

		if (failCount1 > 0 ||
			failCount2 > 0 ||
			failCount3 > 0 ) {

			return false;
		} else {

			let $signupForm1 = $("#signup-form-1");

			$.ajax({
				url: "/api/v1/signup/validate-email/",
				data: {
					"email" : $signupForm1.find("#id_email").val()
				},
				type: "GET",
				dataType: "json"
			}).done(function(response) {

				if (!response.is_user || response.account_type == "consumer") {

					let data = {
						"first_name": $signupForm1.find("#id_first_name").val(),
						"last_name": $signupForm1.find("#id_last_name").val(),
						"email": $signupForm1.find("#id_email").val(),
						"password": $signupForm1.find("#id_password").val(),
						"country": $("#basic button").attr("data-val")
					}

					localStorage.setItem("user_profile", JSON.stringify(data));
					console.log(localStorage.getItem('user_profile'));

					let location = window.location;
					if (location.href.indexOf("for-cultivators") !== -1) {
						location.href = "/for-cultivators/sign-up2/";
					}

					if (location.href.indexOf("for-dispensaries") !== -1) {
						location.href = "/for-dispensaries/sign-up2/";
					}
				} else {

					switch (response.account_type) {

						case 'house_account':
							$.pgwModal({
								target: '#house-dialog',
								titleBar: false
							});
							break;
						case 'claimed_account_free':
						case 'paid_account':
							$.pgwModal({
								target: '#non-house-dialog',
								titleBar: false
							});
							break;
						default:
							break;
					}
				}
			});
		}
	});
});

