'use strict';

W.ns('W.pages');

W.pages.StrainSearchWizard3Page = W.pages.StrainSearchBase.extend({

    successURL: '/search/strain/wizard/4/',

    /**
     * Container for benefit objects in format:
     * {
     *  name: 'help-depression',
     *  value: 5
     * }
     */
    selectedBenefits: [],

    /**
     * The last selected benefit on
     */
    currentBenefitName: '',

    popupDismissed: false,

    ui: {
        $btnSkip: $('.btn-skip-3'),
        $btnSubmit: $('.btn-step-3'),
        $strainBenefit: $('.strain-effect'),
        $removeBenefit: $('.removable'),
        $slider: $('.slider')
    },

    init: function init() {
        this.restoreState();
        this.clickStrainBenefit();
        this.clickRemoveBenefit();
        this.clickStep3Submit();
        this.clickStep3Skip();
    },

    restoreState: function restoreState() {
        var that = this,
            step3State = Cookies.get('strains:search:step3');

        if (step3State) {
            step3State = JSON.parse(step3State);

            if (!step3State.skipped) {
                $.each(step3State.benefits, function (index, benefit) {
                    var $effect = $('#{0}'.format(benefit.name)),
                        $parent = $effect.parent(),
                        $importanceValue = $parent.find('.importance-value');

                    $effect.addClass('active');
                    $parent.find('.removable').removeClass('hidden');
                    $importanceValue.removeClass('hidden');
                    $importanceValue.text(benefit.value);
                    that.selectedBenefits.push({
                        name: benefit.name,
                        value: benefit.value
                    });
                });

                if (that.selectedBenefits.length > 0) {
                    that.toggleButtonsAndSliderState();
                    that.currentBenefitName = that.selectedBenefits[that.selectedBenefits.length - 1].name;
                    that.ui.$slider.slider('value', that.selectedBenefits[that.selectedBenefits.length - 1].value);
                }
            }
        }
    },

    clickStrainBenefit: function clickStrainBenefit() {
        var that = this;

        that.ui.$strainBenefit.on('click', function () {
            that.popupDismissed = false;

            var $benefit = $(this),
                benefitName = $benefit.attr('id'),
                presentBenefit = that.selectedBenefits.filter(function (benefit) {
                    return benefit.name === benefitName;
                });

            that.currentBenefitName = benefitName;
            if (presentBenefit.length > 0) {
                that.ui.$slider.slider('value', $benefit.parent().find('.importance-value').text());
                return;
            }

            if (that.selectedBenefits.length <= 4) {
                $benefit.addClass('active');
                $benefit.parent().find('.removable').removeClass('hidden');
                $benefit.parent().find('.importance-value').removeClass('hidden');
                that.selectedBenefits.push({
                    name: $benefit.attr('id'),
                    value: 1
                });
            }

            if (that.selectedBenefits.length === 5) {
                var $strainBenefits = that.ui.$strainBenefit;
                for (var i = 0; i < $strainBenefits.length; i++) {
                    var $el = $($strainBenefits[i]);
                    if (!$el.hasClass('active')) {
                        $el.addClass('disabled');
                    }
                }
            }

            that.toggleButtonsAndSliderState();
        });
    },

    toggleButtonsAndSliderState: function toggleButtonsAndSliderState() {
        if (this.selectedBenefits.length > 0) {
            this.activateSlider();
            this.ui.$btnSubmit.removeAttr('disabled');
            this.ui.$btnSkip.attr('disabled', 'disabled');
        } else {
            this.regions.$sliderWrapper.addClass('hidden');
        }
    },

    clickRemoveBenefit: function clickRemoveBenefit() {
        var that = this;

        that.ui.$removeBenefit.on('click', function () {
            var $benefitCloseBtn = $(this),
                $benefit = $benefitCloseBtn.parent().find('.strain-effect'),
                $importanceValue = $benefitCloseBtn.parent().find('.importance-value'),
                benefitName = $benefit.attr('id');

            $benefit.removeClass('active');
            $benefitCloseBtn.addClass('hidden');
            $importanceValue.addClass('hidden');
            $importanceValue.text(1);

            for (var i = 0; i < that.selectedBenefits.length; i++) {
                if (that.selectedBenefits[i].name === benefitName) {
                    that.selectedBenefits.splice(i, 1);
                    break;
                }
            }

            if (that.selectedBenefits.length < 5) {
                var $strainBenefits = that.ui.$strainBenefit;
                for (var j = 0; j < $strainBenefits.length; j++) {
                    $($strainBenefits[j]).removeClass('disabled');
                }
            }

            if (that.selectedBenefits.length === 0) {
                that.regions.$sliderWrapper.addClass('hidden');
                that.currentBenefitName = '';
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
        this.selectedBenefits.forEach(function (benefit) {
            if (benefit.name === that.currentBenefitName) {
                var sliderValue = ui.value,
                    $benefitValue = $('#' + that.currentBenefitName).parent().find('.importance-value');
                benefit.value = sliderValue;
                $benefitValue.text(sliderValue);
            }
        });
    },

    clickStep3Submit: function clickStep3Submit() {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();

            var doNotShowAgainCookie = Cookies.get('strains:search:donotshowagain'),
                showDialog = !doNotShowAgainCookie || doNotShowAgainCookie === 'false';

            if (that.selectedBenefits[that.selectedBenefits.length - 1].value === 1 && !that.popupDismissed && showDialog) {
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
                    step: 3,
                    benefits: that.selectedBenefits
                };
                Cookies.set('strains:search:step3', data);
                that.sendDataToWizard(data, that.successURL);
            }
        });
    },

    clickStep3Skip: function clickStep3Skip() {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            var data = {step: 3, skipped: true};
            Cookies.set('strains:search:step3', data);
            that.sendDataToWizard(data, that.successURL);
        });
    }
});
