'use strict';

/* Calling bluesnap.submitCredentials: function that submits card data to BlueSnap, where it will be associated with token, and calls input function with card data object if submission was successful */
function do_when_clicking_submit_button() {
	bluesnap.submitCredentials(function(callback) {
		if (null != callback.error) {
			var errorArray = callback.error;
			for (var i in errorArray) {
				$("#" + errorArray[i].tagId + "-help").text(errorArray[i].errorCode + " - " + errorArray[i].errorDescription); 
			}
		} else {
			var cardData = callback.cardData;
			console.log(
				"Card Type: " +
				cardData.ccType +
				" Last 4 Digits: " +
				cardData.last4Digits +
				" Issuing Country: " +
				cardData.issuingCountry +
				" Is Regulated Card: " +
				cardData.isRegulatedCard + 
				" Card Sub Type: " + 
				cardData.cardSubType + 
				" Bin Category: " +
				cardData.binCategory +    
				" Exp: " +
				cardData.exp +
				" after that I can call final submit"
			);
			var expDate = cardData.exp
			// This is where you would perform final submission to your server

			let $signupCompleteForm = $("#form-signup-complete");
			let data = {};
			let user_profile = localStorage.getItem('user_profile');
			for(var item in data){
				if(data[item].name == 'business_type'){
					data[item].value = parseInt($('input[name=business_type]:checked').attr('data-id'));
				}
				if(data[item].name == 'promo_code'){
					data[item].value = parseInt($("[name=promo_code]").val());
				}
			}
			data["user_profile"] = JSON.parse(user_profile)
			let business_details = {
				"name": $signupCompleteForm.find("[name=name]").val(),
				"phone_number": $signupCompleteForm.find("[name=phone_number]").val(),
				"street_address": $signupCompleteForm.find("[name=street_address]").val(),
				"zip_code": $signupCompleteForm.find("[name=zip_code]").val(),
				"city": $signupCompleteForm.find("[name=city]").val(),
				"state_or_province": $signupCompleteForm.find("[name=state_or_province]").val(),
				"business_type": parseInt($('input[name=business_type]:checked').attr('data-id')),
				"promo_code": parseInt($("[name=promo_code]").val()),
				"security_code": parseInt($("#cvv").text()),
				"exp_date": expDate,
				"plan_type": "BASIC"		// BASIC Billing Plan
			}
			data["business_details"] = business_details
			data['pftoken'] = localStorage.getItem('pftoken')
			data['amount'] = $(".total span").text()
			localStorage.setItem("business_details", JSON.stringify(business_details));
			$("#loading-spinner").show();
			$.ajax({
				url: $signupCompleteForm.attr("action"),
				data: JSON.stringify(data),
				type: "POST",
				dataType: "json",
				contentType: "application/json"
			}).done(function(response){
				$("#loading-spinner").hide();
				window.location.href = "/signup/confirm/";
			}).fail(function(response){
				$("#loading-spinner").hide();
				$("#error_container").empty().hide();
				let error_text = "";
				$.map(response.responseJSON, function(el){
				error_text+= '<p class="e-error">'+el+'</p>';
				});
                $("#error_container").html(error_text).show();
                $.pgwModal({
                    target: '#error-dialog',
                    title: 'Errors!'
                });
			});
		}
	});
}

function loadBusinessTypes(){
	$.ajax({
		url: "/api/v1/signup/business-types/",
		type: "GET",
		dataType: "json"
	}).done(function(response){
		$(".business-type").append(
			`<div class="toggle-button" style="display: none"><div class="btn-group btn-group-toggle" data-toggle="buttons"></div></div>`
		);
		$.map(response, function(obj) {
			$(".btn-group-toggle").append(
				`
				<label class="btn btn-pill btn-outline-primary business_type" data-id="${obj.id}">
					<input type="radio" name="business_type_mobile" autocomplete="off"> ${obj.name}
				</label>
				`
			);
			$(".business-type").append(
				`<label class="business-type-not-mobile"><input type="radio" name="business_type" class="business_type" value="${obj.id}" data-id="${obj.id}"> ${obj.name}</label>`
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

$(document).ready(function() {

    $('input[name="phone_number"]').mask('(000)000-0000');
	if(localStorage.getItem('user_profile') === null) {
		location.href = "/";
	}
	else {
		bluesnap.hostedPaymentFieldsCreation(localStorage.getItem('pftoken'), bsObj);
	}

	// Load business types on page load.
	loadBusinessTypes();
	$('#exp-span').css("padding-top", "9px");

	$("#complete-btn").click(function(e) {
		var failCount1 = 0;
		$(".step-2 input").each(function() {
			var element = $(this);
			if($.trim($(this).val()) === "" && !$(this).hasClass('promo-code-value')) {
                $(this).addClass("error");
                if($(this).hasClass('step2-business-name')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter the name of your business.');
                }
                if($(this).hasClass('step2-phone-number')) {
                    $(this).parent().find('.signup-helper-text').html('Please correct your phone number.');
                }
                if($(this).hasClass('step2-address')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid address.');
                }
                if($(this).hasClass('step2-zip-code')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid zip code.');
                }
                if($(this).hasClass('step2-city')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid address.');
                }
                if($(this).hasClass('step2-state')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid state or province.');
                }
                if($(this).hasClass('step2-card-name')) {
                    $(this).parent().find('.signup-helper-text').html('Please enter a valid name on card.');
                }
				failCount1++;
			}
			else {
				$(this).removeClass("error");
				$(this).parent().find('.signup-helper-text').html('');
			}
		});

		if($(".business-type-not-mobile input:radio").is(":checked")) {
			$(".business-type .signup-helper-text").html('');
		} else {
			$(".business-type .signup-helper-text").html('Please select a business type');
		}

		if(failCount1 == 0) {
			do_when_clicking_submit_button();
		}
	});

	$(document).on("click", ".business_type", function(e){
		$(this).parent().parent().find('.signup-helper-text').html('');
		var type_id = $(this).attr("data-id");
		$('.business-type-not-mobile input[type=radio]').each(function() {
			if($(this).attr('data-id') == type_id) {
				$(this).prop('checked', true);
			} else {
				$(this).prop('checked', false);
			}
		});
		$('.btn-group .btn-outline-primary').each(function() {
			if($(this).attr('data-id') == type_id) {
				$(this).button('toggle');
			}
		});
		let whatYouGetContainer = "div.business-type-"+type_id;
		$(whatYouGetContainer).show();
		$("div[class*=business-type-]").not(whatYouGetContainer).hide();
	});

	$("#id_promo_code").keyup(function() {
		if($("#id_promo_code").val() == '') {
			$(".your-order h3:eq(1)").html('1 Month StrainRx subscription');
			$(".total span").html('$79');
			$("#id_promo_code_value").val('');
		}
	});
	
	$("#id_promo_code").autocomplete({
		source: function(request){
			$(".your-order h3:eq(1)").html('1 Month StrainRx subscription');
			$(".total span").html('$79');
			$("#id_promo_code_value").val('');
			$.ajax({
				url: "/api/v1/signup/search/promocodes/",
				type: "GET",
				dataType: "json",
				data: request,
				success: function(resp){
					$(".your-order h3:eq(1)").html(resp.promo_code.description);
					$(".total span").html('$'+resp.promo_code.amount);
					$("#id_promo_code_value").val(resp.promo_code.id);
				}
			});
		}
	});

});
