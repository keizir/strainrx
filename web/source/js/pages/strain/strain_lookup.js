'use strict';

W.ns('W.pages.strain');

W.pages.strain.StrainLookup = Class.extend({

    init: function init(options) {
        this.onArrowUp = options && options.onArrowUp;
        this.onArrowDown = options && options.onArrowDown;
        this.onReturn = options && options.onReturn;

        this.changeLookupInput();
        this.clickOutsidePayloadArea();
    },

    changeLookupInput: function changeLookupInput() {
        var that = this;
        $('.lookup-input').on('keyup', function (e) {
            var text = $(this).val(),
                $payloadsRegion = $('.payloads-region'),
                $activePayload = $payloadsRegion.find('.search-payload.active'),
                $firstPayload = $payloadsRegion.find('.search-payload:nth-child(1)'),
                $lastPayload = $payloadsRegion.find('.search-payload:last-child');

            if (e.keyCode === 38) { // Up Arrow Key
                that.onArrowUpKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (e.keyCode === 40) { // Down Arrow Key
                that.onArrowDownKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (e.keyCode === 13) { // Enter Key
                that.onEnterKeyPress(e, $activePayload, $firstPayload, $lastPayload);
                return;
            }

            if (text && text.length >= 1) {
                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/strain/lookup/?q={0}'.format(text),
                    success: function (data) {
                        $payloadsRegion.html('');
                        $payloadsRegion.append(that.buildPayloadLookupArea(data));

                        $('.search-payload').on('click', function () {
                            var $payloadSpan = $(this),
                                $lookupInput = $('.lookup-input');
                            $lookupInput.attr('payload-id', $payloadSpan.attr('id'));
                            $lookupInput.attr('payload-slug', $payloadSpan.attr('slug'));
                            $lookupInput.attr('payload-variety', $payloadSpan.attr('variety'));
                            $lookupInput.val($payloadSpan.text());
                            $payloadsRegion.html('');
                        });
                    }
                });
            } else {
                $payloadsRegion.html('');
            }
        });
    },

    onArrowUpKeyPress: function onArrowUpKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        if (this.onArrowUp) {
            this.onArrowUp($activePayload, $firstPayload, $lastPayload);
            return;
        }

        if ($activePayload && $activePayload.length > 0) {
            if ($activePayload.prev().length > 0) {
                $activePayload.removeClass('active');
                $activePayload.prev().addClass('active');
            }
        } else {
            $lastPayload.addClass('active');
        }
    },

    onArrowDownKeyPress: function onArrowDownKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        if (this.onArrowDown) {
            this.onArrowDown($activePayload, $firstPayload, $lastPayload);
            return;
        }

        if ($activePayload && $activePayload.length > 0) {
            if ($activePayload.next().length > 0) {
                $activePayload.removeClass('active');
                $activePayload.next().addClass('active');
            }
        } else {
            $firstPayload.addClass('active');
        }
    },

    onEnterKeyPress: function onEnterKeyPress(e, $activePayload, $firstPayload, $lastPayload) {
        e.preventDefault();

        if (this.onReturn) {
            this.onReturn($activePayload, $firstPayload, $lastPayload);
            return;
        }

        if ($activePayload && $activePayload.length > 0) {
            var $lookupInput = $('.lookup-input'),
                $payloadsRegion = $('.payloads-region');
            $lookupInput.attr('payload-id', $activePayload.attr('id'));
            $lookupInput.attr('payload-slug', $activePayload.attr('slug'));
            $lookupInput.attr('payload-variety', $activePayload.attr('variety'));
            $lookupInput.val($activePayload.text());
            $payloadsRegion.html('');
        }
    },

    buildPayloadLookupArea: function buildPayloadLookupArea(data) {
        if (data) {
            var totalResults = data.total,
                payloads = data.payloads,
                itemHtml = '<span class="search-payload" id="{0}" slug="{1}" variety="{2}">{3}</span>',
                payloadHtml = '';

            if (totalResults && totalResults > 0) {
                $.each(payloads, function (index, payload) {
                    payloadHtml += itemHtml.format(payload.id, payload.strain_slug, payload.variety, payload.name);
                });
                return payloadHtml;
            }
        }
    },

    clickOutsidePayloadArea: function clickOutsidePayloadArea() {
        $(document).on('click', function (e) {
            var elem = $(e.target);
            if (!(elem.parents('.payloads-region').length)) {
                $('.payloads-region').html('');
            }
        });
    }
});
