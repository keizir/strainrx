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

    ui: {
        $btnSkip: $('.btn-skip-2'),
        $btnSubmit: $('.btn-step-2'),
        $strainEffect: $('.strain-effect'),
        $removeEffect: $('.removable'),
        $slider: $('.slider')
    },

    init: function () {
        this.clickStrainEffectListener();
        this.clickRemoveEffectListener();
        this.registerStep2ClickListener();
        this.registerStep2SkipClickListener();
    },

    clickStrainEffectListener: function () {
        var that = this;

        that.ui.$strainEffect.on('click', function () {
            var $effect = $(this),
                effectName = $effect.attr('id'),
                presentEffect = that.selectedEffects.filter(function (effect) {
                    return effect.name === effectName;
                });

            if (presentEffect.length > 0) {
                that.currentEffectName = effectName;
                that.ui.$slider.slider('value', $effect.parent().find('.importance-value').text());
                return;
            }

            $effect.addClass('active');
            $effect.parent().find('.removable').removeClass('hidden');
            $effect.parent().find('.importance-value').removeClass('hidden');
            that.currentEffectName = effectName;
            that.selectedEffects.push({
                name: $effect.attr('id'),
                value: 1
            });

            if (that.selectedEffects.length > 0) {
                that.activateSlider();
                that.ui.$btnSubmit.removeAttr('disabled');
                that.ui.$btnSkip.attr('disabled', 'disabled');
            } else {
                that.regions.$sliderWrapper.addClass('hidden');
            }
        });
    },

    clickRemoveEffectListener: function () {
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
    handleSlideChange: function (ui) {
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

    registerStep2ClickListener: function () {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();
            var doNotShowAgainCookie = Cookies.get('strains:search:donotshowagain'),
                doNotShowAgain = !doNotShowAgainCookie || doNotShowAgainCookie === 'false';
            if (that.selectedEffects.length === 1 && that.selectedEffects[0].value === 1 && doNotShowAgain) {
                var $justASecondDialog = $('.just-a-second-dialog');
                $justASecondDialog.find('.dismiss-btn').on('click', function () {
                    $justASecondDialog.dialog('close');
                });

                W.common.Dialog($justASecondDialog, function () {
                    Cookies.set('strains:search:donotshowagain', $('#do-not-show-again').is(':checked'));
                });
            } else {
                that.sendDataToWizard({
                    step: 2,
                    effects: that.selectedEffects
                }, that.successURL);
            }
        });
    },

    registerStep2SkipClickListener: function () {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 2, skipped: true}, that.successURL);
        });
    }
});
