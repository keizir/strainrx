'use strict';

W.ns('W.pages');

W.pages.StrainSearchWizard4Page = W.pages.StrainSearchBase.extend({

    successURL: '/search/strain/results/',

    /**
     * Container for side effect objects in format:
     * {
     *  name: 'help-depression',
     *  value: 5
     * }
     */
    selectedSideEffects: [],

    /**
     * The last selected side effect on
     */
    currentSideEffectName: '',

    ui: {
        $btnSkip: $('.btn-skip-4'),
        $btnSubmit: $('.btn-step-4'),
        $strainSideEffect: $('.strain-effect'),
        $removeSideEffect: $('.removable'),
        $slider: $('.slider')
    },

    init: function () {
        this.clickStrainSideEffectListener();
        this.clickRemoveSideEffectListener();
        this.registerStep4ClickListener();
        this.registerStep4SkipClickListener();
    },

    clickStrainSideEffectListener: function () {
        var that = this;

        that.ui.$strainSideEffect.on('click', function () {
            var $sideEffect = $(this),
                sideEffectName = $sideEffect.attr('id'),
                presentSideEffect = that.selectedSideEffects.filter(function (sideEffect) {
                    return sideEffect.name === sideEffectName;
                });

            if (presentSideEffect.length > 0) {
                that.currentSideEffectName = sideEffectName;
                that.ui.$slider.slider('value', $sideEffect.parent().find('.importance-value').text());
                return;
            }

            $sideEffect.addClass('active');
            $sideEffect.parent().find('.removable').removeClass('hidden');
            $sideEffect.parent().find('.importance-value').removeClass('hidden');
            that.currentSideEffectName = sideEffectName;
            that.selectedSideEffects.push({
                name: $sideEffect.attr('id'),
                value: 1
            });

            if (that.selectedSideEffects.length > 0) {
                that.activateSlider();
                that.ui.$btnSubmit.removeAttr('disabled');
                that.ui.$btnSkip.attr('disabled', 'disabled');
            } else {
                that.regions.$sliderWrapper.addClass('hidden');
            }
        });
    },

    clickRemoveSideEffectListener: function () {
        var that = this;

        that.ui.$removeSideEffect.on('click', function () {
            var $sideEffectCloseBtn = $(this),
                $sideEffect = $sideEffectCloseBtn.parent().find('.strain-effect'),
                $importanceValue = $sideEffectCloseBtn.parent().find('.importance-value'),
                sideEffectName = $sideEffect.attr('id');

            $sideEffect.removeClass('active');
            $sideEffectCloseBtn.addClass('hidden');
            $importanceValue.addClass('hidden');
            $importanceValue.text(1);

            for (var i = 0; i < that.selectedSideEffects.length; i++) {
                if (that.selectedSideEffects[i].name === sideEffectName) {
                    that.selectedSideEffects.splice(i, 1);
                    break;
                }
            }


            if (that.selectedSideEffects.length === 0) {
                that.regions.$sliderWrapper.addClass('hidden');
                that.currentSideEffectName = '';
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
        this.selectedSideEffects.forEach(function (sideEffect) {
            if (sideEffect.name === that.currentSideEffectName) {
                var sliderValue = ui.value,
                    $sideEffectValue = $('#' + that.currentSideEffectName).parent().find('.importance-value');
                sideEffect.value = sliderValue;
                $sideEffectValue.text(sliderValue);
            }
        });
    },

    registerStep4ClickListener: function () {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();
            var doNotShowAgainCookie = Cookies.get('strains:search:donotshowagain'),
                doNotShowAgain = !doNotShowAgainCookie || doNotShowAgainCookie === 'false';
            if (that.selectedSideEffects.length === 1 && that.selectedSideEffects[0].value === 1 && doNotShowAgain) {
                var $justASecondDialog = $('.just-a-second-dialog');
                $justASecondDialog.find('.dismiss-btn').on('click', function () {
                    $justASecondDialog.dialog('close');
                });

                W.common.Dialog($justASecondDialog, function () {
                    Cookies.set('strains:search:donotshowagain', $('#do-not-show-again').is(':checked'));
                });
            } else {
                that.sendDataToWizard({
                    step: 4,
                    sideEffects: that.selectedSideEffects
                }, that.successURL);
            }
        });
    },

    registerStep4SkipClickListener: function () {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 4, skipped: true}, that.successURL);
        });
    }
});
