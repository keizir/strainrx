'use strict';

W.ns('W.pages');

W.pages.StrainSearchBase = Class.extend({

    regions: {
        $sliderWrapper: $('.slider-wrapper')
    },

    activateSlider: function () {
        var that = this;
        this.regions.$sliderWrapper.removeClass('hidden');
        this.ui.$slider.slider({
            value: 1,
            min: 1,
            max: 5,
            step: 1,
            slide: function (event, ui) {
                that.handleSlideChange(ui)
            }
        });
    },

    handleSlideChange: function (ui) {
        // intentionally left as empty. Should be overrided in child views.
    },

    sendDataToWizard: function (data, successUrl) {
        $.ajax({
            method: 'POST',
            url: '/api/v1/search/strain',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                window.location.href = successUrl;
            },
            error: function (error) {
                if (error.status === 400) {
                    $('.error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });
    }
});
