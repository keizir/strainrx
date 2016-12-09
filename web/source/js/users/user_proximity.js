'use strict';

W.ns('W.users');

W.users.ProximityPage = Class.extend({

    defaultProximityValue: 10,

    ui: {
        $userId: $('.user-id')
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
                $('.ui-slider-handle').text('{0} MI'.format(ui.value));
                that.proximity = ui.value;
            }
        });

        $('.ui-slider-handle').text('{0} MI'.format(this.proximity || this.defaultProximityValue));
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
