'use strict';

W.ns('W.common');

W.common.Dialog = function ($el, closeCallback) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 450,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "500px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.ConfirmDialog = function ($el, closeCallback) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 250,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "500px");
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};

W.common.RateDialog = function ($el, closeCallback) {
    if ($el) {
        $el.removeClass('hidden');
        $el.dialog({
            closeOnEscape: true,
            height: 400,
            width: 'auto',
            modal: true,
            draggable: false,
            resizable: false,
            create: function () {
                $(this).css("maxWidth", "450px");

                var $rateStarsRegion = $('.rate-stars');
                if ($rateStarsRegion) {
                    $rateStarsRegion.rateYo({
                        spacing: '10px',
                        starWidth: '50px',
                        maxValue: 5,
                        precision: 1,
                        halfStar: true,
                        normalFill: '#f4f4f4', // $white-smoke
                        ratedFill: '#6bc331', // $avocado-green
                        onSet: function () {
                            var $errorMessageRegion = $('.error-message');
                            if ($errorMessageRegion) {
                                $errorMessageRegion.text('');
                            }
                        }
                    });
                }
            },
            close: function (e, ui) {
                if (closeCallback) {
                    closeCallback(e, ui);
                }
            }
        });
    }
};
