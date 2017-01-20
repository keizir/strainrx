'use strict';

W.ns('W.users');

W.users.ProximityPage = Class.extend({

    defaultProximityValue: 10,

    ui: {
        $userId: $('.user-id'),
        $proximityInput: $('.proximity-value')
    },

    init: function (options) {
        this.proximity = options && options.proximity;

        this.initSlider();
        this.updateProximity();
    },

    initSlider: function initSlider() {
        var that = this;
        $('.slider').slider({
            range: 'min',
            value: that.proximity || that.defaultProximityValue,
            min: 0, max: 50, step: 0.5,
            slide: function (event, ui) {
                that.setSliderHandleValue(ui.value);
                that.proximity = ui.value;
                that.ui.$proximityInput.val(ui.value);
            }
        });

        this.setSliderHandleValue(this.proximity || this.defaultProximityValue);
        this.initProximityInput();
    },

    initProximityInput: function initProximityInput() {
        var that = this;
        $('.proximity-value').on('focusout', function () {
            var $input = $(this),
                $inputVal = $input.val();

            if ($inputVal) {
                $inputVal = parseFloat($inputVal).toFixed(1);
                $('.slider').slider('value', $inputVal);
                that.proximity = $inputVal;
            } else {
                that.setProximityValue(0);
            }

            if ($inputVal && $inputVal < 0) {
                that.setProximityValue(0);

            }

            if ($inputVal && $inputVal > 50) {
                that.setProximityValue(50);
            }
        });
    },

    setProximityValue: function setProximityValue(value) {
        $('.slider').slider('value', value);
        this.setSliderHandleValue(value);
        $('.proximity-value').val(value);
        this.proximity = value;
    },

    setSliderHandleValue: function setSliderHandleValue(value) {
        $('.proximity-value').off('focusout');
        $('.ui-slider-handle').html('<input type="number" class="proximity-value" value="{0}">'.format(value));
        this.initProximityInput();
    },

    updateProximity: function updateProximity() {
        var that = this;
        $('.btn-update-proximity').on('click', function () {
            $.ajax({
                method: 'POST',
                url: '/api/v1/users/{0}/proximity'.format(that.ui.$userId.val()),
                dataType: 'json',
                data: JSON.stringify({'proximity': that.proximity}),
                success: function () {
                    window.location.reload();
                }
            });
        });
    }

});
