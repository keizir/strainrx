'use strict';

W.ns('W.pages.dispensary');

W.pages.dispensary.DispensaryLookup = Class.extend({

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
                url = $payloadsRegion.find('.search-payload.active').attr('url'),
                business_id = $payloadsRegion.find('.search-payload.active').attr('business_id'),
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
                that.onEnterKeyPress(e, url, text, business_id);
                return;
            }

            if (text && text.length >= 1) {
                var locTime = DispensaryPage.getDispLocationTime();

                $.ajax({
                    method: 'GET',
                    url: '/api/v1/search/dispensary/lookup/?q={query}&loc={loc}&tz={tz}'.format({
                        query: text,
                        loc: encodeURIComponent(JSON.stringify(locTime.location)),
                        tz: encodeURIComponent(JSON.stringify(locTime.timezone))
                    }),
                    success: function (data) {
                        $payloadsRegion.html('');
                        $payloadsRegion.append(that.buildPayloadLookupArea(data));

                        $('.search-payload').on('click', function () {
                            var $payloadSpan = $(this),
                                $lookupInput = $('.lookup-input');
                            $lookupInput.attr('payload-id', $payloadSpan.attr('id'));
                            $lookupInput.val($payloadSpan.text());
                            $payloadsRegion.html('');
                            $payloadsRegion.hide();
                        });
                    }
                });
            } else {
                $payloadsRegion.html('');
                $payloadsRegion.hide();
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

    onEnterKeyPress: function onEnterKeyPress(e, url, text, business_id) {
        e.preventDefault();

        if (url && text) {
            var $lookupInput = $('.lookup-input'),
                $payloadsRegion = $('.payloads-region');

            $lookupInput.attr('payload-url', url);
            $lookupInput.attr('business_id', business_id);
            $lookupInput.val(text);
            $payloadsRegion.html('');
            $payloadsRegion.hide();
        }
    },

    buildPayloadLookupArea: function buildPayloadLookupArea(data) {
        if (data) {
            var totalResults = data.total,
                payloads = data.payloads,
                itemHtml = '<span class="search-payload" id="{id}" url="{url}" business_id="{business_id}" name="{name}"><img width="20" height="20" src="{img_src}"/><span class="disp-name">{name}</span> ({loc}) {dist} {open}</span>',
                payloadHtml = '';

            if (totalResults && totalResults > 0) {
                $.each(payloads, function (index, payload) {
                    payloadHtml += itemHtml.format({
                        'id': payload.business_location_id,
                        'img_src': payload.image || '{0}images/default-location-image.jpeg'.format(STATIC_URL),
                        'url': payload.url,
                        'name': payload.location_name,
                        'open': (payload.open) ? 'Open' : 'Closed',
                        'loc': '{0}, {1}'.format(payload.city, payload.state),
                        'dist': (payload.distance) ? '{0} Miles'.format(Math.round(payload.distance * 10) / 10) : '',
                        'business_id': payload.business_id
                    });
                });

                $('.payloads-region').show();

                return payloadHtml;
            }
        } else {
            $('.payloads-region').hide();
        }
    },

    clickOutsidePayloadArea: function clickOutsidePayloadArea() {
        var that = this;

        $(document).on('click', function (e) {
            var elem = $(e.target);

            if (elem.hasClass('search-payload')) {
                // click on autocomplete result
                var url = elem.attr('url'),
                    text = elem.attr('name'),
                    business_id = elem.attr('business_id');

                that.onEnterKeyPress(e, url, text, business_id);
            } else if (!(elem.parents('.payloads-region').length)) {
                $('.payloads-region').html('');
                $('.payloads-region').hide();
            }
        });
    }
});
