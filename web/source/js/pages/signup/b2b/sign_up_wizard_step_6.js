'use strict';

W.ns('W.pages.b2b');

W.pages.b2b.SignUpWizardStep6 = W.common.WizardStep.extend({

    init: function init(options) {
        this._super({
            step: 6,
            model: options && options.model,
            submit_el: '.btn-b2b-step-6',
            template_el: '#b2b-wizard-6'
        });
    },

    renderHTML: function () {
        return this.$template({
            days: W.common.Constants.days,
            renderHours: _.template($('#operational-hours').html())
        });
    },

    initEventHandlers: function initEventHandlers() {
        this._super();

        var timeMask = W.common.Constants.masks.time;

        $('input[name="mon_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="mon_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="tue_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="tue_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="wed_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="wed_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="thu_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="thu_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="fri_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="fri_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="sat_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="sat_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="sun_open"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
        $('input[name="sun_close"]').mask(timeMask.mask, {placeholder: timeMask.placeholder});
    },

    validate: function validate() {
        var that = this,
            dayInvalid = false,
            isOpenBeforeClose = function isOpenBeforeClose(open, close) {
                if (open && close) {
                    var o = new Date(Date.parse('1/1/1970 {0}'.format(open))),
                        c = new Date(Date.parse('1/1/1970 {0}'.format(close)));
                    return o < c;
                }
                return true;
            };

        $.each(W.common.Constants.days, function (index, day) {
            var openTime = that.getOpenTime(day.value),
                closeTime = that.getCloseTime(day.value);

            if (!isOpenBeforeClose(openTime, closeTime)) {
                $('.error-message').text('{0} close time cannot be earlier than open time'.format(day.name));
                dayInvalid = true;
            }

            if (openTime && !openTime.split(' ')[1]) {
                $('.error-message').text('{0} open time should have AM/PM specified'.format(day.name));
                dayInvalid = true;
            }

            if (closeTime && !closeTime.split(' ')[1]) {
                $('.error-message').text('{0} close time should have AM/PM specified'.format(day.name));
                dayInvalid = true;
            }

            if ((openTime && !closeTime) || (!openTime && closeTime)) {
                $('.error-message').text('{0} should have both open and close time selected.'.format(day.name));
                dayInvalid = true;
            }

            if (openTime) {
                var oTime = openTime.split(' ')[0],
                    oParts = oTime.split(':');

                if (!oParts || oParts.length <= 1) {
                    $('.error-message').text('{0} open time should be in HH:MM format'.format(day.name));
                    dayInvalid = true;
                }
            }

            if (closeTime) {
                var cTime = closeTime.split(' ')[0],
                    cParts = cTime.split(':');

                if (!cParts || cParts.length <= 1) {
                    $('.error-message').text('{0} close time should be in HH:MM format'.format(day.name));
                    dayInvalid = true;
                }
            }
        });

        return !dayInvalid;
    },

    getOpenTime: function getOpenTime(day) {
        var time = $('input[name="{0}_open"]'.format(day)).val(),
            amPm = $('select[name="{0}_open_am_pm"]'.format(day)).val();
        return time ? '{0} {1}'.format(time, amPm) : null;
    },

    getCloseTime: function getCloseTime(day) {
        var time = $('input[name="{0}_close"]'.format(day)).val(),
            amPm = $('select[name="{0}_close_am_pm"]'.format(day)).val();
        return time ? '{0} {1}'.format(time, amPm) : null;
    },

    submit: function submit() {
        var data = {
            mon: {open: this.getOpenTime('mon'), close: this.getCloseTime('mon')},
            tue: {open: this.getOpenTime('tue'), close: this.getCloseTime('tue')},
            wed: {open: this.getOpenTime('wed'), close: this.getCloseTime('wed')},
            thu: {open: this.getOpenTime('thu'), close: this.getCloseTime('thu')},
            fri: {open: this.getOpenTime('fri'), close: this.getCloseTime('fri')},
            sat: {open: this.getOpenTime('sat'), close: this.getCloseTime('sat')},
            sun: {open: this.getOpenTime('sun'), close: this.getCloseTime('sun')}
        };

        $.publish('update_step_data', {step: this.step, data: data});
        $.publish('show_step', {step: 7});
    },

    restoreState: function restoreState() {
        if (this.model.get(this.step)) {
            var state = this.model.get(this.step);

            findAndSelect('mon_open', state.mon.open);
            findAndSelect('mon_close', state.mon.close);
            selectIsClosed('mon');

            findAndSelect('tue_open', state.tue.open);
            findAndSelect('tue_close', state.tue.close);
            selectIsClosed('tue');

            findAndSelect('wed_open', state.wed.open);
            findAndSelect('wed_close', state.wed.close);
            selectIsClosed('wed');

            findAndSelect('thu_open', state.thu.open);
            findAndSelect('thu_close', state.thu.close);
            selectIsClosed('thu');

            findAndSelect('fri_open', state.fri.open);
            findAndSelect('fri_close', state.fri.close);
            selectIsClosed('fri');

            findAndSelect('sat_open', state.sat.open);
            findAndSelect('sat_close', state.sat.close);
            selectIsClosed('sat');

            findAndSelect('sun_open', state.sun.open);
            findAndSelect('sun_close', state.sun.close);
            selectIsClosed('sun');
        }

        function findAndSelect(selectName, hoursValue) {
            var $input = $('input[name="{0}"]'.format(selectName)),
                $select = $('select[name="{0}_am_pm"]'.format(selectName)),
                valueSplit, time, timeAmPm;

            if (hoursValue) {
                valueSplit = hoursValue.split(' ');
                time = valueSplit[0];
                timeAmPm = valueSplit[1];
                $input.val(time);
                $select.find('option[value="{0}"]'.format(timeAmPm)).prop('selected', 'selected');
            }
        }

        function selectIsClosed(day) {
            var $isClosed = $('input[name="{0}_is_closed"]'.format(day)),
                $open = $('input[name="{0}_open"]'.format(day)),
                $close = $('input[name="{0}_close"]'.format(day));

            if (!$open.val() && !$close.val()) {
                $isClosed.attr('checked', true);
            }

            $open.on('focusout', function () {
                if ($(this).val()) {
                    $isClosed.attr('checked', false);
                } else {
                    $isClosed.attr('checked', true);
                }
            });

            $close.on('focusout', function () {
                if ($(this).val()) {
                    $isClosed.attr('checked', false);
                } else {
                    $isClosed.attr('checked', true);
                }
            });
        }
    }

});