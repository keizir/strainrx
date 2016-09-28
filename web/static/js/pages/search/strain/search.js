'use strict';

W.ns('W.pages');

W.pages.StrainSearchPage = Class.extend({

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
        $slider: $('.slider'),
        $strainEffect: $('.strain-effect'),
        $removeEffect: $('.removable')
    },

    regions: {
        $sliderWrapper: $('.slider-wrapper')
    },

    init: function () {
        this.clickStrainEffectListener();
        this.clickRemoveEffectListener();

        this.registerStep1ClickListener();
        this.registerStep1SkipClickListener();

        this.registerStep2ClickListener();
        this.registerStep2SkipClickListener();

        this.registerStep3ClickListener();
        this.registerStep3SkipClickListener();

        this.registerStep4ClickListener();
        this.registerStep4SkipClickListener();
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
                return;
            }

            $effect.addClass('active');
            $effect.parent().find('.removable').removeClass('hidden');
            that.currentEffectName = effectName;
            that.selectedEffects.push({
                name: $effect.attr('id'),
                value: 1
            });

            if (that.selectedEffects.length > 0) {
                that.activateSlider();
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
                effectName = $effect.attr('id');

            $effect.removeClass('active');
            $effectCloseBtn.addClass('hidden');

            for (var i = 0; i < that.selectedEffects.length; i++) {
                if (that.selectedEffects[i].name === effectName) {
                    that.selectedEffects.splice(i, 1);
                    break;
                }
            }


            if (that.selectedEffects.length === 0) {
                that.regions.$sliderWrapper.addClass('hidden');
                that.currentEffectName = '';
            }
        });
    },

    activateSlider: function () {
        var that = this;

        this.regions.$sliderWrapper.removeClass('hidden');
        this.ui.$slider.slider({
            value: 1,
            min: 1,
            max: 5,
            step: 1,
            slide: function (event, ui) {
                that.selectedEffects.forEach(function (effect) {
                    if (effect.name === that.currentEffectName) {
                        effect.value = ui.value;
                    }
                });
            }
        });
    },

    registerStep1ClickListener: function () {
        var that = this;
        $('.btn-step-1').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 1,
                sativa: $('input[name="sativa"]').is(":checked"),
                hybrid: $('input[name="hybrid"]').is(":checked"),
                indica: $('input[name="indica"]').is(":checked")
            }, '/search/strain/wizard/2/');
        });
    },

    registerStep1SkipClickListener: function () {
        var that = this;
        $('.btn-skip-1').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 1, skipped: true}, '/search/strain/wizard/2/');
        });
    },

    registerStep2ClickListener: function () {
        var that = this;
        $('.btn-step-2').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 2
            }, '/search/strain/wizard/3/');
        });
    },

    registerStep2SkipClickListener: function () {
        var that = this;
        $('.btn-skip-2').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 2, skipped: true}, '/search/strain/wizard/3/');
        });
    },

    registerStep3ClickListener: function () {
        var that = this;
        $('.btn-step-3').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 3
            }, '/search/strain/wizard/4/');
        });
    },

    registerStep3SkipClickListener: function () {
        var that = this;
        $('.btn-skip-3').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 3, skipped: true}, '/search/strain/wizard/4/');
        });
    },

    registerStep4ClickListener: function () {
        var that = this;
        $('.btn-step-4').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({
                step: 4
            }, '/search/strain/results/');
        });
    },

    registerStep4SkipClickListener: function () {
        var that = this;
        $('.btn-skip-4').on('click', function (e) {
            e.preventDefault();
            that.sendDataToWizard({step: 4, skipped: true}, '/search/strain/results/');
        });
    },

    sendDataToWizard: function (data, successUrl) {
        $.ajax({
            method: 'POST',
            url: '/api/v1/search/strain',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                window.location.href = successUrl;
            },
            error: function (error) {
                if (error.status === 400) {
                    $('.error-message').text(JSON.parse(error.responseText).error);
                }
            }
        });
    }
});
