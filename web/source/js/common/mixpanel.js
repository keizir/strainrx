'use strict';

W.ns('W.common');

W.common.Mixpanel = {

    track: function track(eventName, eventData) {
        if (mixpanel) {
            try {
                mixpanel.track(eventName, eventData);
            } catch (error) {
                console.error('Mixpanel: cannot log an event. Error message: [{0}].'.format(err.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    }

};
