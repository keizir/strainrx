'use strict';

W.ns('W.pages.search.strain');

W.pages.search.strain.SearchWizardStep = W.common.WizardStep.extend({

    currentEffectName: '',
    popupDismissed: false,
    settingName_NeverShowPopupAgain: 'search_strain_donotshowagain',

    init: function init(options) {
        this._super({
            step: options.step,
            model: options && options.model,
            submit_el: options && options.submit_el,
            template_el: options && options.template_el
        });

        this.currentUserId = options && options.currentUserId;
        this.skip_el = options && options.skip_el;
        this.back_el = options && options.back_el;
    },

    initEventHandlers: function initEventHandlers() {
        var that = this;

        $(this.submit_el).on('click', function (e) {
            e.preventDefault();
            if (that.validate()) {
                that.submit();
            }
        });

        $(this.skip_el).on('click', function (e) {
            e.preventDefault();
            that.skip();
        });

        $(this.back_el).on('click', function (e) {
            e.preventDefault();
            that.back();
        });
    },

    validate: function validate() {
        return true;
    },

    skip: function skip() {
        throw new Error('Child class must implement skip.');
    },

    back: function back() {
        throw new Error('Child class must implement back before use.');
    },

    restoreState: function restoreState() {
        throw new Error('Child class must implement restoreState.');
    },

    showDialogOrProceed: function showDialogOrProceed(container, proceedCallback) {
        var that = this;
        W.users.UserSettings.get(that.currentUserId, that.settingName_NeverShowPopupAgain, function (setting) {
            var doNotShowAgain = setting && setting.doNotShowAgain;
            if (container[container.length - 1].value === 1 && !that.popupDismissed && !doNotShowAgain) {
                that.showJustASecondDialog();
            } else {
                proceedCallback();
            }
        });
    },

    showJustASecondDialog: function showJustASecondDialog() {
        var that = this,
            $justASecondDialog = $('.just-a-second-dialog');

        $justASecondDialog.find('.dismiss-btn').on('click', function () {
            $justASecondDialog.dialog('close');
            that.popupDismissed = true;
        });

        W.common.Dialog($justASecondDialog, function () {
            that.popupDismissed = false;
            W.users.UserSettings.update(that.currentUserId, that.settingName_NeverShowPopupAgain, {
                doNotShowAgain: $('#do-not-show-again').is(':checked')
            });
        });
    },

    restoreEffectsState: function restoreEffectsState(step, container) {
        var state = this.model.get(step);
        if (!state || state.skipped) {
            return;
        }

        container.length = 0;

        var that = this;
        $.each(state.effects, function (index, effect) {
            var $effect = $('#{0}'.format(effect.name)),
                $parent = $effect.parent(),
                $importanceValue = $parent.find('.importance-value');

            $effect.addClass('active');
            $parent.find('.removable').removeClass('hidden');
            $importanceValue.removeClass('hidden');
            $importanceValue.text(effect.value);
            container.push({
                name: effect.name,
                value: effect.value
            });
        });

        if (container.length > 0) {
            that.toggleButtonsAndSliderState(container);
            that.currentEffectName = container[container.length - 1].name;
            $('.slider').slider('value', container[container.length - 1].value);
        }

        if (step !== 4 && container.length === 5) {
            that.disableNotActiveEffects();
        }
    },

    toggleButtonsAndSliderState: function toggleButtonsAndSliderState(container) {
        if (container.length > 0) {
            this.activateSlider(container);
            $(this.submit_el).removeAttr('disabled');
            $(this.skip_el).attr('disabled', 'disabled');
        } else {
            $('.slider-wrapper').addClass('hidden');
        }
    },

    isStepSkipped: function isStepSkipped(step) {
        var data = this.model.get(step);
        return data && data.skipped;
    },

    activateSlider: function activateSlider(container) {
        var that = this;
        $('.slider-wrapper').removeClass('hidden');
        $('.slider').slider({
            value: 1, min: 1, max: 5, step: 1,
            slide: function (event, ui) {
                that.handleSlideChange(ui.value, container)
            }
        });
    },

    handleSlideChange: function handleSlideChange(value, container) {
        var that = this;
        container.forEach(function (effect) {
            if (effect.name === that.currentEffectName) {
                var $effectValue = $('#' + that.currentEffectName).parent().find('.importance-value');
                effect.value = value;
                $effectValue.text(value);
            }
        });
    },

    disableNotActiveEffects: function disableNotActiveEffects() {
        var $strainEffects = $('.strain-effect');
        for (var i = 0; i < $strainEffects.length; i++) {
            var $el = $($strainEffects[i]);
            if (!$el.hasClass('active')) {
                $el.addClass('disabled');
            }
        }
    },

    clickStrainEffect: function clickStrainEffect(container) {
        var that = this;
        $('.strain-effect').on('click', function () {
            that.popupDismissed = false;

            var $effect = $(this),
                effectName = $effect.attr('id'),
                presentEffect = container.filter(function (effect) {
                    return effect.name === effectName;
                });

            that.currentEffectName = effectName;
            if (presentEffect.length > 0) {
                $('.slider').slider('value', $effect.parent().find('.importance-value').text());
                return;
            }

            if (container.length <= 4) {
                $effect.addClass('active');
                $effect.parent().find('.removable').removeClass('hidden');
                $effect.parent().find('.importance-value').removeClass('hidden');
                container.push({
                    name: $effect.attr('id'),
                    value: 1
                });
            }

            if (container.length === 5) {
                that.disableNotActiveEffects();
            }

            if (container.length === 0 && that.isStepSkipped(2)) {
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).attr('disabled', 'disabled');
            }

            that.toggleButtonsAndSliderState(container);
        });
    },

    clickRemoveEffect: function clickRemoveEffect(container) {
        var that = this;
        $('.removable').on('click', function () {
            var $effectCloseBtn = $(this),
                $effect = $effectCloseBtn.parent().find('.strain-effect'),
                $importanceValue = $effectCloseBtn.parent().find('.importance-value'),
                effectName = $effect.attr('id');

            $effect.removeClass('active');
            $effectCloseBtn.addClass('hidden');
            $importanceValue.addClass('hidden');
            $importanceValue.text(that.step === 4 ? 5 : 1);

            for (var i = 0; i < container.length; i++) {
                if (container[i].name === effectName) {
                    container.splice(i, 1);
                    break;
                }
            }

            if (container.length < 5) {
                var $strainEffects = $('.strain-effect');
                for (var j = 0; j < $strainEffects.length; j++) {
                    $($strainEffects[j]).removeClass('disabled');
                }
            }

            if (container.length === 0) {
                $('.slider-wrapper').addClass('hidden');
                that.currentEffectName = '';
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).removeAttr('disabled');
            }

            if (that.step === 3 && that.isStepSkipped(2)) {
                $(that.submit_el).attr('disabled', 'disabled');
                $(that.skip_el).attr('disabled', 'disabled');
            }
        });
    }

});