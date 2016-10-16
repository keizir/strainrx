'use strict';

W.ns('W.pages');

W.pages.StrainSearchWizard2Page = W.pages.StrainSearchBase.extend({

    successURL: '/search/strain/wizard/3/',

    /**
     * Container for effect objects in format:
     * {
     *  name: 'happy',
     *  value: 3
     * }
     */
    selectedEffects: [],

    /**
     * The last selected effect on
     */
    currentEffectName: '',

    popupDismissed: false,

    ui: {
        $btnSkip: $('.btn-skip-2'),
        $btnSubmit: $('.btn-step-2'),
        $strainEffect: $('.strain-effect'),
        $removeEffect: $('.removable'),
        $slider: $('.slider')
    },

    init: function init() {
        this.restoreState();
        this.clickStrainEffect();
        this.clickRemoveEffect();
        this.clickStep2Submit();
        this.clickStep2Skip();
    },

    restoreState: function restoreState() {
        var that = this,
            step2State = Cookies.get('strains:search:step2');

        if (step2State) {
            step2State = JSON.parse(step2State);

            if (!step2State.skipped) {
                $.each(step2State.effects, function (index, effect) {
                    var $effect = $('#{0}'.format(effect.name)),
                        $parent = $effect.parent(),
                        $importanceValue = $parent.find('.importance-value');

                    $effect.addClass('active');
                    $parent.find('.removable').removeClass('hidden');
                    $importanceValue.removeClass('hidden');
                    $importanceValue.text(effect.value);
                    that.selectedEffects.push({
                        name: effect.name,
                        value: effect.value
                    });
                });

                if (that.selectedEffects.length > 0) {
                    that.toggleButtonsAndSliderState();
                    that.currentEffectName = that.selectedEffects[that.selectedEffects.length - 1].name;
                    that.ui.$slider.slider('value', that.selectedEffects[that.selectedEffects.length - 1].value);
                }
            }
        }
    },

    clickStrainEffect: function clickStrainEffect() {
        var that = this;

        that.ui.$strainEffect.on('click', function () {
            that.popupDismissed = false;

            var $effect = $(this),
                effectName = $effect.attr('id'),
                presentEffect = that.selectedEffects.filter(function (effect) {
                    return effect.name === effectName;
                });

            that.currentEffectName = effectName;
            if (presentEffect.length > 0) {
                that.ui.$slider.slider('value', $effect.parent().find('.importance-value').text());
                return;
            }

            if (that.selectedEffects.length <= 4) {
                $effect.addClass('active');
                $effect.parent().find('.removable').removeClass('hidden');
                $effect.parent().find('.importance-value').removeClass('hidden');
                that.selectedEffects.push({
                    name: $effect.attr('id'),
                    value: 1
                });
            }

            if (that.selectedEffects.length === 5) {
                var $strainEffects = that.ui.$strainEffect;
                for (var i = 0; i < $strainEffects.length; i++) {
                    var $el = $($strainEffects[i]);
                    if (!$el.hasClass('active')) {
                        $el.addClass('disabled');
                    }
                }
            }

            that.toggleButtonsAndSliderState();
        });
    },

    toggleButtonsAndSliderState: function toggleButtonsAndSliderState() {
        if (this.selectedEffects.length > 0) {
            this.activateSlider();
            this.ui.$btnSubmit.removeAttr('disabled');
            this.ui.$btnSkip.attr('disabled', 'disabled');
        } else {
            this.regions.$sliderWrapper.addClass('hidden');
        }
    },

    clickRemoveEffect: function clickRemoveEffect() {
        var that = this;

        that.ui.$removeEffect.on('click', function () {
            var $effectCloseBtn = $(this),
                $effect = $effectCloseBtn.parent().find('.strain-effect'),
                $importanceValue = $effectCloseBtn.parent().find('.importance-value'),
                effectName = $effect.attr('id');

            $effect.removeClass('active');
            $effectCloseBtn.addClass('hidden');
            $importanceValue.addClass('hidden');
            $importanceValue.text(1);

            for (var i = 0; i < that.selectedEffects.length; i++) {
                if (that.selectedEffects[i].name === effectName) {
                    that.selectedEffects.splice(i, 1);
                    break;
                }
            }

            if (that.selectedEffects.length < 5) {
                var $strainEffects = that.ui.$strainEffect;
                for (var j = 0; j < $strainEffects.length; j++) {
                    $($strainEffects[j]).removeClass('disabled');
                }
            }

            if (that.selectedEffects.length === 0) {
                that.regions.$sliderWrapper.addClass('hidden');
                that.currentEffectName = '';
                that.ui.$btnSubmit.attr('disabled', 'disabled');
                that.ui.$btnSkip.removeAttr('disabled');
            }
        });
    },

    /**
     * Override from parent view. Used in parent
     * @param ui
     */
    handleSlideChange: function handleSlideChange(ui) {
        var that = this;
        this.selectedEffects.forEach(function (effect) {
            if (effect.name === that.currentEffectName) {
                var sliderValue = ui.value,
                    $effectValue = $('#' + that.currentEffectName).parent().find('.importance-value');
                effect.value = sliderValue;
                $effectValue.text(sliderValue);
            }
        });
    },

    clickStep2Submit: function clickStep2Submit() {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();

            var doNotShowAgainCookie = Cookies.get('strains:search:donotshowagain'),
                showDialog = !doNotShowAgainCookie || doNotShowAgainCookie === 'false';

            if (that.selectedEffects[that.selectedEffects.length - 1].value === 1 && !that.popupDismissed && showDialog) {
                var $justASecondDialog = $('.just-a-second-dialog');
                $justASecondDialog.find('.dismiss-btn').on('click', function () {
                    $justASecondDialog.dialog('close');
                    that.popupDismissed = true;
                });

                W.common.Dialog($justASecondDialog, function () {
                    that.popupDismissed = false;
                    Cookies.set('strains:search:donotshowagain', $('#do-not-show-again').is(':checked'));
                });
            } else {
                var data = {
                    step: 2,
                    effects: that.selectedEffects
                };

                Cookies.set('strains:search:step2', data);
                that.sendDataToWizard(data, that.successURL);
            }
        });
    },

    clickStep2Skip: function clickStep2Skip() {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            var data = {step: 2, skipped: true};
            Cookies.set('strains:search:step2', data);
            that.sendDataToWizard(data, that.successURL);
        });
    }
});
