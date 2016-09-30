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

    ui: {
        $btnSkip: $('.btn-skip-3'),
        $btnSubmit: $('.btn-step-3'),
        $strainBenefit: $('.strain-effect'),
        $removeBenefit: $('.removable'),
        $slider: $('.slider')
    },

    init: function () {
        this.clickStrainBenefitListener();
        this.clickRemoveBenefitListener();
        this.registerStep3ClickListener();
        this.registerStep3SkipClickListener();
    },

    clickStrainBenefitListener: function () {
        var that = this;

        that.ui.$strainBenefit.on('click', function () {
            var $benefit = $(this),
                benefitName = $benefit.attr('id'),
                presentBenefit = that.selectedBenefits.filter(function (benefit) {
                    return benefit.name === benefitName;
                });

            if (presentBenefit.length > 0) {
                that.currentBenefitName = benefitName;
                that.ui.$slider.slider('value', $benefit.parent().find('.importance-value').text());
                return;
            }

            $benefit.addClass('active');
            $benefit.parent().find('.removable').removeClass('hidden');
            $benefit.parent().find('.importance-value').removeClass('hidden');
            that.currentBenefitName = benefitName;
            that.selectedBenefits.push({
                name: $benefit.attr('id'),
                value: 1
            });

            if (that.selectedBenefits.length > 0) {
                that.activateSlider();
                that.ui.$btnSubmit.removeAttr('disabled');
                that.ui.$btnSkip.attr('disabled', 'disabled');
            } else {
                that.regions.$sliderWrapper.addClass('hidden');
            }
        });
    },

    clickRemoveBenefitListener: function () {
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
    handleSlideChange: function (ui) {
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

    registerStep3ClickListener: function () {
        var that = this;
        this.ui.$btnSubmit.on('click', function (e) {
            e.preventDefault();
            var doNotShowAgainCookie = Cookies.get('strains:search:donotshowagain'),
                doNotShowAgain = !doNotShowAgainCookie || doNotShowAgainCookie === 'false';
            if (that.selectedBenefits.length === 1 && that.selectedBenefits[0].value === 1 && doNotShowAgain) {
                var $justASecondDialog = $('.just-a-second-dialog');
                $justASecondDialog.find('.dismiss-btn').on('click', function () {
                    $justASecondDialog.dialog('close');
                });

                W.common.Dialog($justASecondDialog, function () {
                    Cookies.set('strains:search:donotshowagain', $('#do-not-show-again').is(':checked'));
                });
            } else {
                that.sendDataToWizard({
                    step: 3,
                    benefits: that.selectedBenefits
                }, that.successURL);
            }
        });
    },

    registerStep3SkipClickListener: function () {
        var that = this;
        this.ui.$btnSkip.on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 3, skipped: true}, that.successURL);
        });
    }
});
