'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizard = W.common.Wizard.extend({

    steps: {},

    init: function init(options) {
        this._super({
            model: options && options.model
        });

        this.name = 'SignUpWizard';
        this.showStep({step: 1});

        W.subscribe.apply(this);
    },

    _on_show_step: function _on_show_step(ev, data) {
        this.showStep({step: data.step});
    },

    _on_update_step_data: function _on_update_step_data(ev, data) {
        this.updateData(data);
    },

    _on_submit_form: function _on_submit_form(ev, data) {
        var that = this;
        $.ajax({
            method: 'POST',
            url: '/api/v1/businesses/signup',
            dataType: 'json',
            data: that.prepareSubmitFormData(data),
            success: function (successData) {
                that.uploadImage(data, successData);
            },
            error: function (error) {
                if (error.status === 400) {
                    $('.error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });
    },

    prepareSubmitFormData: function prepareSubmitFormData(data) {
        return JSON.stringify({
            name: data[1].business_name,
            email: data[2].user_email,
            pwd: data[3].pwd, pwd2: data[3].pwd2,
            dispensary: data[4].dispensary, delivery: data[4].delivery,
            street1: data[5].address, city: data[5].city, state: data[5].state, zip_code: data[5].zipcode,
            phone: data[5].phone, ext: data[5].ext,
            mon_open: data[6].mon.open, mon_close: data[6].mon.close,
            tue_open: data[6].tue.open, tue_close: data[6].tue.close,
            wed_open: data[6].wed.open, wed_close: data[6].wed.close,
            thu_open: data[6].thu.open, thu_close: data[6].thu.close,
            fri_open: data[6].fri.open, fri_close: data[6].fri.close,
            sat_open: data[6].sat.open, sat_close: data[6].sat.close,
            sun_open: data[6].sun.open, sun_close: data[6].sun.close,
            certified_legal_compliance: data[8].certified_legal_compliance,
            is_terms_accepted: data[9].terms
        })
    },

    uploadImage: function uploadImage(data, successData) {
        var imageFile = data[7]; //file
        if (imageFile && !imageFile.skipped) {
            $.ajax({
                type: 'POST',
                url: '/api/v1/businesses/{0}/image'.format(successData.business_id),
                enctype: 'multipart/form-data',
                data: imageFile,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': W.getCookie('csrftoken')
                },
                success: function () {
                    window.location.href = '/businesses/signup/done/';
                },
                error: function () {
                    // Anyway redirect to next page even if image failed to save
                    window.location.href = '/businesses/signup/done/?image=fail';
                }
            });
        }
    },

    initSteps: function initSteps() {
        this.steps[1] = new W.pages.b2b.SignUpWizardStep1({model: this.model});
        this.steps[2] = new W.pages.b2b.SignUpWizardStep2({model: this.model});
        this.steps[3] = new W.pages.b2b.SignUpWizardStep3({model: this.model});
        this.steps[4] = new W.pages.b2b.SignUpWizardStep4({model: this.model});
        this.steps[5] = new W.pages.b2b.SignUpWizardStep5({model: this.model});
        this.steps[6] = new W.pages.b2b.SignUpWizardStep6({model: this.model});
        this.steps[7] = new W.pages.b2b.SignUpWizardStep7({model: this.model});
        this.steps[8] = new W.pages.b2b.SignUpWizardStep8({model: this.model});
        this.steps[9] = new W.pages.b2b.SignUpWizardStep9({model: this.model});
    },

    showStep: function showStep(data) {
        this.destroy();

        var step = this.steps[data.step];
        this.show(step);
        this.handleStepClick(data.step);

        if (step.restoreState) {
            step.restoreState();
        }
    },

    updateData: function updateData(data) {
        this.model.set(data.step, data.data);
    }

});
