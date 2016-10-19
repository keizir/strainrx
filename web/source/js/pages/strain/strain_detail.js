'use strict';

W.ns('W.pages');

W.pages.StrainDetailPage = Class.extend({

    effectNames: W.common.Constants.effectNames,
    benefitNames: W.common.Constants.benefitNames,
    sideEffectNames: W.common.Constants.sideEffectNames,
    flavorsNames: W.common.Constants.flavors,

    ui: {
        $strainId: $('.strain-id'),
        $strainRatingStars: $('.strain-rating-stars'),
        $strainLike: $('.strain-like'),

        $effectsRegion: $('.effects-region'),
        $benefitsRegion: $('.benefits-region'),
        $sideEffectsRegion: $('.side-effects-region'),
        $flavorsRegion: $('.flavors-region'),

        $addPhotoLink: $('.add-photo-link'),

        $menuExpander: $('.menu-expander'),
        $menuLocations: $('.locations'),
        $menuFilter: $('.filter-menu'),
        $menuLink: $('.menu-link'),
        $priceExpander: $('.price-expander')
    },

    init: function init() {
        this.initRating();

        this.strainLikeHover();
        this.strainLikeClick();

        this.populateEffects();
        this.populateBenefits();
        this.populateSideEffects();
        this.populateFlavors();

        this.uploadPhotoListener();
        this.buildLocationsMenu();
    },

    initRating: function initRating() {
        var value = this.ui.$strainRatingStars.text();
        this.ui.$strainRatingStars.rateYo({
            rating: value,
            readOnly: true,
            spacing: '1px',
            normalFill: '#aaa8a8', // $grey-light
            ratedFill: '#6bc331', // $avocado-green
            starWidth: '16px'
        });
    },

    strainLikeHover: function strainLikeHover() {
        this.ui.$strainLike.mouseenter(function () {
            var $el = $(this);
            if (!$el.hasClass('active')) {
                $el.removeClass('fa-heart-o');
                $el.addClass('fa-heart');
                $el.addClass('heart-active');
            }
        });

        this.ui.$strainLike.mouseleave(function () {
            var $el = $(this);
            if (!$el.hasClass('active')) {
                $el.addClass('fa-heart-o');
                $el.removeClass('fa-heart');
                $el.removeClass('heart-active');
            }
        });
    },

    strainLikeClick: function strainLikeClick() {
        var that = this;

        this.ui.$strainLike.on('click', function () {
            var $el = $(this);
            if ($el.hasClass('active')) {
                that.likeStrain({
                    like: false
                }, function () {
                    $el.addClass('fa-heart-o');
                    $el.removeClass('fa-heart');
                    $el.removeClass('heart-active');
                    $el.removeClass('active');
                });
            } else {
                that.likeStrain({
                    like: true
                }, function () {
                    $el.removeClass('fa-heart-o');
                    $el.addClass('fa-heart');
                    $el.addClass('heart-active');
                    $el.addClass('active');
                });
            }
        });
    },

    likeStrain: function likeStrain(data, successCallback) {
        $.ajax({
            method: 'POST',
            url: '/api/v1/search/strain/like',
            dataType: 'json',
            data: JSON.stringify(data),
            success: function () {
                if (successCallback) {
                    successCallback();
                }
            }
        });
    },

    populateEffects: function populateEffects() {
        var that = this,
            effectsJsonString = this.ui.$effectsRegion.text().replace(/'/g, '\"'),
            effectsJson = JSON.parse(effectsJsonString),
            effectsToDisplay = [];

        this.ui.$effectsRegion.text('');

        $.each(effectsJson, function (name, value) {
            if (value > 0) {
                effectsToDisplay.push({
                    name: that.effectNames[name],
                    value: value
                });
            }
        });

        effectsToDisplay.sort(this.sortValues);
        this.ui.$effectsRegion.append(this.effectHtml(effectsToDisplay));
    },

    populateBenefits: function populateBenefits() {
        var that = this,
            benefitsJsonString = this.ui.$benefitsRegion.text().replace(/'/g, '\"'),
            benefitsJson = JSON.parse(benefitsJsonString),
            benefitsToDisplay = [];

        this.ui.$benefitsRegion.text('');

        $.each(benefitsJson, function (name, value) {
            if (value > 0) {
                benefitsToDisplay.push({
                    name: that.benefitNames[name],
                    value: value
                });
            }
        });

        benefitsToDisplay.sort(this.sortValues);
        this.ui.$benefitsRegion.append(this.effectHtml(benefitsToDisplay));
    },

    populateSideEffects: function populateSideEffects() {
        var that = this,
            sideEffectsJsonString = this.ui.$sideEffectsRegion.text().replace(/'/g, '\"'),
            sideEffectsJson = JSON.parse(sideEffectsJsonString),
            sideEffectsToDisplay = [];

        this.ui.$sideEffectsRegion.text('');

        $.each(sideEffectsJson, function (name, value) {
            if (value > 0) {
                sideEffectsToDisplay.push({
                    name: that.sideEffectNames[name],
                    value: value
                });
            }
        });

        sideEffectsToDisplay.sort(this.sortValues);
        this.ui.$sideEffectsRegion.append(this.sideEffectHtml(sideEffectsToDisplay));
    },

    populateFlavors: function populateFlavors() {
        var that = this,
            flavorsJsonString = this.ui.$flavorsRegion.text().replace(/'/g, '\"'),
            flavorsJson = JSON.parse(flavorsJsonString),
            flavorsToDisplay = [];

        this.ui.$flavorsRegion.text('');

        $.each(flavorsJson, function (name, value) {
            if (value > 0) {
                var flavor = that.flavorsNames[name];
                flavorsToDisplay.push({
                    name: flavor.name,
                    img: '<img src="{0}{1}"/>'.format(STATIC_URL, flavor.image),
                    value: value
                });
            }
        });

        flavorsToDisplay.sort(this.sortValues);
        this.ui.$flavorsRegion.append(this.flavorsHtml(flavorsToDisplay));
    },

    sortValues: function sortValues(el1, el2) {
        var aName = el1.name, bName = el2.name,
            aValue = el1.value, bValue = el2.value;
        return aValue > bValue ? -1 : aValue < bValue ? 1 : aName < bName ? -1 : aName > bName ? 1 : 0;
    },

    effectHtml: function effectHtml(toDisplay) {
        var effectHtml = '<div class="effects-wrapper">';

        $.each(toDisplay, function (index, effect) {
            effectHtml += '<div class="effect-wrapper">';
            effectHtml += '<span class="effect-name">' + effect.name + '</span>';
            effectHtml += '<div class="effect">';

            if (effect.value >= 5) {
                effectHtml += '<span class="fill fill-5"></span>';
            }

            if (effect.value === 4) {
                effectHtml += '<span class="fill fill-4"></span>';
            }

            if (effect.value === 3) {
                effectHtml += '<span class="fill fill-3"></span>';
            }

            if (effect.value === 2) {
                effectHtml += '<span class="fill fill-2"></span>';
            }

            if (effect.value === 1) {
                effectHtml += '<span class="fill fill-1"></span>';
            }

            effectHtml += '</div></div>';
        });

        effectHtml += '</div>';
        return effectHtml;
    },

    sideEffectHtml: function sideEffectHtml(toDisplay) {
        var effectHtml = '<div class="effects-wrapper">';

        $.each(toDisplay, function (index, effect) {
            effectHtml += '<div class="effect-wrapper">';
            effectHtml += '<span class="effect-name">' + effect.name + '</span>';
            effectHtml += '<div class="effect">';

            if (effect.value === 10) {
                effectHtml += '<span class="fill fill-5"></span>';
            }

            if (effect.value === 9) {
                effectHtml += '<span class="fill fill-4"></span>';
            }

            if (effect.value === 8) {
                effectHtml += '<span class="fill fill-3"></span>';
            }

            if (effect.value === 7) {
                effectHtml += '<span class="fill fill-2"></span>';
            }

            if (effect.value === 6) {
                effectHtml += '<span class="fill fill-1"></span>';
            }

            effectHtml += '</div></div>';
        });

        effectHtml += '</div>';
        return effectHtml;
    },

    flavorsHtml: function flavorsHtml(toDisplay) {
        var html = '<div class="flavors-wrapper">';

        $.each(toDisplay, function (index, flavor) {
            html += '<div class="flavor-wrapper">';
            html += '<div class="flavor">';
            html += flavor.img;
            html += '</div>';
            html += '<span class="flavor-name">' + flavor.name + '</span>';
            html += '</div>';
        });

        html += '</div>';
        return html;
    },

    uploadPhotoListener: function uploadPhotoListener() {
        var that = this;

        this.ui.$addPhotoLink.on('click', function (e) {
            e.preventDefault();
            W.common.Dialog($('.upload-image-dialog'));

            $('.image-upload-form').on('submit', function (e) {
                e.preventDefault();
                $('.loader').removeClass('hidden');
                $('.btn-upload-image-submit').addClass('hidden');

                var file = $('.upload-image')[0].files[0],
                    formData = new FormData();

                formData.append('file', file);
                formData.append('name', file.name);

                $.ajax({
                    type: 'POST',
                    url: '/api/v1/search/strain/{0}/image'.format(that.ui.$strainId.val()),
                    enctype: 'multipart/form-data',
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function () {
                        $('.loader').addClass('hidden');
                        $('.btn-upload-image-submit').removeClass('hidden');
                        $('.upload-image-dialog').dialog('close');
                    }
                });
            });
        });
    },

    buildLocationsMenu: function buildLocationsMenu() {
        var that = this;

        that.ui.$menuExpander.on('click', function () {
            that.ui.$menuLocations.toggleClass('hidden');
            that.ui.$menuFilter.toggleClass('expanded');
        });

        that.ui.$menuFilter.mouseleave(function () {
            that.ui.$menuLocations.addClass('hidden');
            that.ui.$menuFilter.removeClass('expanded');
        });

        that.ui.$menuLink.on('click', function (e) {
            e.preventDefault();
            that.ui.$menuActiveLink.text($(this).find('a').text());
            that.ui.$menuFilter.removeClass('expanded');
            that.ui.$menuLocations.addClass('hidden');
        });

        that.ui.$priceExpander.on('click', function () {
            $('.prices-wrapper').toggleClass('hidden');
        });

        $('.prices-wrapper').mouseleave(function () {
            $(this).addClass('hidden');
        });

        $('.price').on('click', function () {
            $('.prices-wrapper').addClass('hidden');
            var priceType = $(this).attr('id');
            $('.price-value').each(function (index, $el) {
                var $price = $($el);
                if ($price.attr('id') === priceType) {
                    $price.addClass('active');
                } else {
                    $price.removeClass('active');
                }
            });
        });

        $('.dispensary-rating').each(function () {
            var $this = $(this),
                rating = $this.text();

            $this.rateYo({
                rating: rating,
                readOnly: true,
                spacing: '1px',
                normalFill: '#aaa8a8', // $grey-light
                ratedFill: '#6bc331', // $avocado-green
                starWidth: '16px'
            });
        });
    }
});
