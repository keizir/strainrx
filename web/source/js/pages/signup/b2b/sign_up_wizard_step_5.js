'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep5 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 5,
            model: options && options.model,
            submit_el: '.btn-b2b-step-5',
            template_el: '#b2b-wizard-5'
        });
    },

    renderHTML: function () {
        var stepData = this.model.get(this.step);
        return this.$template({
            address: stepData && stepData.address,
            city: stepData && stepData.city,
            state: stepData && stepData.state,
            zipcode: stepData && stepData.zipcode,
            phone: stepData && stepData.phone,
            ext: stepData && stepData.ext
        });
    },

    validate: function validate() {
        var address = $('input[name="address"]').val(),
            city = $('input[name="city"]').val(),
            state = $('input[name="state"]').val(),
            zipCode = $('input[name="zipcode"]').val(),
            phoneNumber = $('input[name="phone"]').val(),
            phoneExt = $('input[name="ext"]').val();

        function validateLength(value, fieldDisplayName) {
            if (!value || value.trim().length === 0) {
                $('.error-message').text('{0} is required'.format(fieldDisplayName));
                return false;
            }

            return true;
        }

        if (!validateLength(address, 'Address') || !validateLength(city, 'City') || !validateLength(state, 'State') || !validateLength(zipCode, 'Zip Code') || !validateLength(phoneNumber, 'Phone Number')) {
            return false;
        }

        if (!W.common.Constants.regex.onlyAlpha.test(city)) {
            $('.error-message').text('City name cannot contain a numbers');
            return false;
        }

        if (state.length > 2 || state.length < 2 || !W.common.Constants.regex.onlyAlpha.test(state)) {
            $('.error-message').text('Enter a valid state abbreviation');
            return false;
        }

        if (phoneExt && !W.common.Constants.regex.onlyNumeric.test(phoneExt)) {
            $('.error-message').text('Extension must contain only numbers');
            return false;
        }

        return true;
    },

    submit: function submit() {
        var data = {
            address: $('input[name="address"]').val().trim(),
            city: $('input[name="city"]').val().trim(),
            state: $('input[name="state"]').val().trim(),
            zipcode: $('input[name="zipcode"]').val().trim(),
            phone: $('input[name="phone"]').val().trim(),
            ext: $('input[name="ext"]').val()
        };
        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 6});
    }

});