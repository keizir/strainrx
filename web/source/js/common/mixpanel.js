'use strict';

W.ns('W.common');

W.common.Mixpanel = {

    track: function track(eventName, eventData) {
        if (window.mixpanel) {
            try {
                window.mixpanel.track(eventName, eventData);
            } catch (error) {
                console.error('Mixpanel: cannot log an event. Error message: [{0}].'.format(error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    alias: function alias(user_id) {
        if (window.mixpanel) {
            try {
                window.mixpanel.alias(user_id);
            } catch (error) {
                console.error('Mixpanel: cannot alias the user {0}. Error message: [{1}].'.format(user_id, error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    },

    identify: function identify(user_id) {
        if (window.mixpanel) {
            try {
                window.mixpanel.identify(user_id);
            } catch (error) {
                console.error('Mixpanel: cannot identify the user {0}. Error message: [{1}].'.format(user_id, error.message));
            }
        } else {
            console.error('Mixpanel: not available.');
        }
    }

};
