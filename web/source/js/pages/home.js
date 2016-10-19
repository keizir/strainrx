'use strict';

W.ns('W.pages');

W.pages.HomePage = Class.extend({

    ui: {
        $lookupInput: $('.lookup-input'),
        $lookupSubmit: $('.lookup-submit'),
        $payloadsRegion: $('.payloads-region')
    },

    init: function init() {
        this.clickLetsGoButton();
        this.changeLookupInput();
        this.clickLookupSubmit();
    },

    changeLookupInput: function changeLookupInput() {
        var that = this;
        this.ui.$lookupInput.on('keyup', function (e) {
            var text = $(this).val(),
                $payloadsRegion = that.ui.$payloadsRegion,
                $activePayload = $payloadsRegion.find('.search-payload.active'),
                $firstPayload = $payloadsRegion.find('.search-payload:nth-child(1)'),
                $lastPayload = $payloadsRegion.find('.search-payload:last-child');

            if (e.keyCode === 38) { // Up Arrow Key
                e.preventDefault();

                if ($activePayload && $activePayload.length > 0) {
                    if ($activePayload.prev().length > 0) {
                        $activePayload.removeClass('active');
                        $activePayload.prev().addClass('active');
                    }
                } else {
                    $lastPayload.addClass('active');
                }

                return;
            }

            if (e.keyCode === 40) { // Down Arrow Key
                e.preventDefault();

                if ($activePayload && $activePayload.length > 0) {
                    if ($activePayload.next().length > 0) {
                        $activePayload.removeClass('active');
                        $activePayload.next().addClass('active');
                    }
                } else {
                    $firstPayload.addClass('active');
                }

                return;
            }

            if (e.keyCode === 13) { // Enter Key
                e.preventDefault();
                if ($activePayload && $activePayload.length > 0) {
                    that.ui.$lookupInput.attr('payload-id', $activePayload.attr('id'));
                    that.ui.$lookupInput.val($activePayload.text());
                    that.ui.$payloadsRegion.html('');
                }
                return;
            }

            if (text && text.length >= 3) {
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/strain/lookup/?q={0}'.format(text),
                    success: function (data) {
                        that.ui.$payloadsRegion.html('');
                        that.ui.$payloadsRegion.append(that.buildPayloadLookupArea(data));

                        $('.search-payload').on('click', function () {
                            var $payloadSpan = $(this);
                            that.ui.$lookupInput.attr('payload-id', $payloadSpan.attr('id'));
                            that.ui.$lookupInput.val($payloadSpan.text());
                            that.ui.$payloadsRegion.html('');
                        });
                    }
                });
            } else {
                that.ui.$payloadsRegion.html('');
            }
        });
    },

    buildPayloadLookupArea: function buildPayloadLookupArea(data) {
        if (data) {
            var totalResults = data.total,
                payloads = data.payloads,
                payloadHtml = '';

            if (totalResults && totalResults > 0) {
                $.each(payloads, function (index, payload) {
                    payloadHtml += '<span class="search-payload" id="' + payload.strain_slug + '">' + payload.name + '</span>';
                });

                return payloadHtml;
            }
        }
    },

    clickLookupSubmit: function clickLookupSubmit() {
        var that = this;
        this.ui.$lookupSubmit.on('click', function (e) {
            e.preventDefault();
            var $input = that.ui.$lookupInput,
                strainName = $input.val(),
                strainSlug = $input.attr('payload-id');

            if (strainName && strainSlug) {
                window.location.href = '/search/strain/{0}'.format(strainSlug);
            }
        });
    }
});
