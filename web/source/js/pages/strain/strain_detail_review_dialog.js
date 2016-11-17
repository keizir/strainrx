'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainReviewDialog = Class.extend({

    reviewEffects: [],

    effectNames: W.common.Constants.effectNames,
    benefitNames: W.common.Constants.benefitNames,
    sideEffectNames: W.common.Constants.sideEffectNames,

    dialogSubtitles: {
        'positive-effects': 'Positive Effects',
        'medical-benefits': 'Medical Benefits',
        'negative-effects': 'Negative Effects'
    },

    init: function init(options) {
        this.model = options && options.model || new W.common.Model();
        this.effectType = null;
        this.clickDisagreeLink();
    },

    clickDisagreeLink: function clickDisagreeLink() {
        var that = this;
        this.strainReviewDialogTemplate = _.template($('#strain_review_dialog_template').html());
        $('.disagree-link').on('click', function (e) {
            e.preventDefault();
            that.buildAndShowReviewDialog($(this));
        });
    },

    buildAndShowReviewDialog: function buildAndShowReviewDialog($link) {
        var that = this,
            effectType = $link.prop('id'),
            parentWidth = $link.parent().outerWidth(true),
            dialogWidth = parseInt(parentWidth, 10) * (parentWidth < 480 ? 1.2 : 0.9),

            effects = 'positive-effects' === effectType ?
                this.model.get('strain').effects :
                'medical-benefits' === effectType ?
                    this.model.get('strain').benefits :
                    this.model.get('strain').side_effects,

            toDisplay = this.buildEffectsToDisplay(effects, 'positive-effects' === effectType ?
                this.effectNames : 'medical-benefits' === effectType ? this.benefitNames : this.sideEffectNames);

        this.effectType = effectType;

        $('.strain-review-dialog-wrapper').html(this.strainReviewDialogTemplate({
            subtitle: this.dialogSubtitles[effectType],
            effects: toDisplay,
            renderReviewEffect: that.renderReviewEffect
        }));

        this.initReviewDialogSliders(effectType);

        W.common.ReviewDialog($('.strain-review-dialog'), function () {
            $('.strain-review-dialog').dialog('destroy');
            that.reviewEffects = [];
        }, {
            width: '{0}px'.format(dialogWidth),
            maxWidth: '{0}px'.format(dialogWidth)
        });

        this.initAddButton(effectType);
        this.clickRemoveEffect($('.remove-effect'));
        this.clickUpdateStrainEffects();
    },

    buildEffectsToDisplay: function buildEffectsToDisplay(rawEffects, effectNames) {
        var effectsToDisplay = [];
        $.each(rawEffects, function (name, value) {
            if (value > 0) {
                effectsToDisplay.push({name: name, displayName: effectNames[name], value: value});
            }
        });
        effectsToDisplay.sort(this.sortValues);
        return effectsToDisplay
    },

    sortValues: function sortValues(el1, el2) {
        var aName = el1.name, bName = el2.name,
            aValue = el1.value, bValue = el2.value;
        return aValue > bValue ? -1 : aValue < bValue ? 1 : aName < bName ? -1 : aName > bName ? 1 : 0;
    },

    renderReviewEffect: function renderReviewEffect(effect) {
        var template = _.template($('#strain_review_dialog_review_effect_template').html());
        return template({effect: effect});
    },

    initReviewDialogSliders: function initReviewDialogSliders(effectType) {
        var that = this;
        $.each($('.review-effect-wrapper'), function () {
            that.initReviewDialogSlider($(this), effectType);
        });

        $('.action-plus').on('click', function () {
            that.increaseEffectValue($(this), effectType);
        });

        $('.action-minus').on('click', function () {
            that.decreaseEffectValue($(this), effectType);
        });
    },

    increaseEffectValue: function increaseEffectValue($actionPlusBtn, effectType) {
        var $reviewEffectSlider = $actionPlusBtn.parent(),
            $effectSlider = $reviewEffectSlider.parent(),
            valueElements = $reviewEffectSlider.find('.value'),
            effectName = $effectSlider.parent().find('.effect-name').prop('id'),
            effectCurrentValue = parseInt($effectSlider.find('.effect-value').text(), 10),
            effectNewValue = this.buildNewIncreaseValue(effectCurrentValue, effectType);

        this.setReviewEffectValue(effectName, effectNewValue);
        $effectSlider.find('.effect-value').text(effectNewValue);

        for (var i = 0; i < valueElements.length; i++) {
            var $el = $(valueElements[i]);
            if (!$el.hasClass('active')) {
                $el.addClass('active');
                break;
            }
        }
    },

    buildNewIncreaseValue: function buildNewIncreaseValue(currentValue, effectType) {
        if (effectType === 'negative-effects') {
            if (currentValue === 0) {
                currentValue = 5;
            }
            return currentValue < 10 ? currentValue + 1 : currentValue;
        }

        return currentValue < 5 ? currentValue + 1 : currentValue;
    },

    decreaseEffectValue: function decreaseEffectValue($actionMinusBtn, effectType) {
        var $reviewEffectSlider = $actionMinusBtn.parent(),
            $effectSlider = $reviewEffectSlider.parent(),
            valueElements = $reviewEffectSlider.find('.value'),
            effectName = $effectSlider.parent().find('.effect-name').prop('id'),
            effectCurrentValue = parseInt($effectSlider.find('.effect-value').text(), 10),
            effectNewValue = this.buildNewDecreaseValue(effectCurrentValue, effectType);

        this.setReviewEffectValue(effectName, effectNewValue);
        $effectSlider.find('.effect-value').text(effectNewValue);

        for (var i = valueElements.length - 1; i >= 0; i--) {
            var $el = $(valueElements[i]);
            if ($el.hasClass('active')) {
                $el.removeClass('active');
                break;
            }
        }
    },

    buildNewDecreaseValue: function buildNewDecreaseValue(currentValue, effectType) {
        if (effectType === 'negative-effects') {
            if (currentValue === 6) {
                currentValue = 0;
            }
            return currentValue > 0 ? currentValue - 1 : currentValue;
        }

        return currentValue > 0 ? currentValue - 1 : currentValue;
    },

    initReviewDialogSlider: function initReviewDialogSlider($reviewEffectWrapper, effectType) {
        var effectName = $reviewEffectWrapper.find('.effect-name').prop('id'),
            effectValue = parseInt($reviewEffectWrapper.find('.effect-slider').find('.effect-value').text(), 10),
            effectSliderTemplate = _.template($('#strain_review_dialog_effect_slider_template').html());

        this.reviewEffects.push({name: effectName, value: effectValue});
        $reviewEffectWrapper.find('.effect-slider').append(effectSliderTemplate({
            value: this.buildDisplayValue(effectValue, effectType)
        }));
    },

    buildDisplayValue: function buildDisplayValue(value, effectType) {
        if (effectType === 'negative-effects') {
            if (value === 6) {
                value = 1;
            }

            if (value === 7) {
                value = 2;
            }

            if (value === 8) {
                value = 3;
            }

            if (value === 9) {
                value = 4;
            }

            if (value === 10) {
                value = 5;
            }
        }

        return value;
    },

    getReviewEffectValue: function (name) {
        var e = null;
        $.each(this.reviewEffects, function (index, effect) {
            if (name === effect.name) {
                e = effect;
            }
        });
        return e;
    },

    setReviewEffectValue: function (name, value) {
        $.each(this.reviewEffects, function (index, effect) {
            if (name === effect.name) {
                effect.value = value;
            }
        });
    },

    initAddButton: function initAddButton(effectType) {
        var that = this;
        this.retrieveEffects(effectType, function (effects) {
            var payloadTemplate = _.template($('#strain_review_dialog_effects_payload_template').html());
            $('.effects-payload').html(payloadTemplate({effects: effects}));

            $('.btn-add-effect').on('click', function (e) {
                e.preventDefault();
                $('.effects-payload').toggleClass('hidden');
                $('.effects-payload-top-border').toggleClass('hidden');
            });

            that.initEffectPayloadEventHandlers();
        });
    },

    retrieveEffects: function retrieveEffects(effectType, success) {
        var type = 'positive-effects' === effectType ?
            'effect' : 'medical-benefits' === effectType ? 'benefit' : 'side_effect';
        $.ajax({
            method: 'GET',
            url: '/api/v1/search/effect/{0}'.format(type),
            success: function (effects) {
                success(effects);
            }
        });
    },

    initEffectPayloadEventHandlers: function initEffectPayloadEventHandlers() {
        var that = this;
        $('.payload-effect').on('click', function () {
            that.selectEffectPayload($(this));
        });
    },

    selectEffectPayload: function selectEffectPayload($activePayload) {
        if ($activePayload && $activePayload.length > 0) {
            var that = this,
                effectName = $activePayload.find('.effect-name').text(),
                effect = this.getReviewEffectValue(effectName);

            if (effect === null) {
                $('.review-effects-holder').append(this.renderReviewEffect({
                    displayName: $activePayload.find('.effect-display-name').text(),
                    name: effectName,
                    value: 0
                }));

                var $reviewEffectWrapper = $('.review-effect-wrapper-{0}'.format(effectName));
                this.initReviewDialogSlider($reviewEffectWrapper, that.effectType);

                $reviewEffectWrapper.find('.action-plus').on('click', function () {
                    that.increaseEffectValue($(this), that.effectType);
                });

                $reviewEffectWrapper.find('.action-minus').on('click', function () {
                    that.decreaseEffectValue($(this), that.effectType);
                });

                $reviewEffectWrapper.find('.remove-effect').on('click', function () {
                    that.removeEffect($(this));
                });
            } else {
                $('#{0}'.format(effectName)).parent().effect("highlight", {color: '#bbe6d1'}, 1000);
            }

            $('.effects-payload').addClass('hidden');
            $('.effects-payload-top-border').addClass('hidden');
        }
    },

    clickRemoveEffect: function clickRemoveEffect($removeEffect) {
        var that = this;
        $removeEffect.on('click', function () {
            that.removeEffect($(this));
        });
    },

    removeEffect: function removeEffect($removeEffect) {
        var effectName = $removeEffect.prop('id');
        for (var i = 0; i < this.reviewEffects.length; i++) {
            if (this.reviewEffects[i].name === effectName) {
                this.reviewEffects.splice(i, 1);
                break;
            }
        }
        $('.review-effect-wrapper-{0}'.format(effectName)).remove();
    },

    clickUpdateStrainEffects: function clickUpdateStrainEffects() {
        var that = this;
        $('.btn-update-effects').on('click', function (e) {
            e.preventDefault();
            console.log(that.reviewEffects); // TODO send via POST when backend is ready
        });
    }
});
