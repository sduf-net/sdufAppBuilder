import AsyncStorage from '@react-native-async-storage/async-storage';
import messaging, { firebase } from '@react-native-firebase/messaging';
import PushNotification from 'react-native-push-notification';
import store from '../redux/store';
import { PermissionsAndroid, Platform } from 'react-native';
import { URL, SOCKET_PROJECT_TOKEN } from '@env';
// import firebase from '@react-native-firebase/app';

const LOCAL_CHANNEL_ID = 'defaultLocalPushesChannelName';

export const initFirebase = async () => {
  const firebaseConfig = {
    apiKey: 'AIzaSyAQGru8i9SeX5iT2xETv5551rFPIqmCa08',
    authDomain: 'sduf-messages.firebaseapp.com',
    databaseURL: 'https://sduf-messages.firebaseio.com', // Add this line
    projectId: 'sduf-messages',
    storageBucket: 'sduf-messages.appspot.com',
    messagingSenderId: '222136333452',
    appId: '1:222136333452:ios:b34bbb02fbdad9a09ff7a9',
    measurementId: '',
  };
  if (!firebase.apps.length) {
    await firebase.initializeApp(firebaseConfig);
  } else {
    firebase.app(); // if already initialized, use that one
  }
};

export const checkApplicationPermission = async () => {
  if (Platform.OS === 'android') {
    try {
      await PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS);
    } catch (error) {
      console.error('[ERROR]', error);
    }
  }
};

export const getFCMToken = async () => {
  let fcmtoken = await AsyncStorage.getItem('fcmtoken');
  if (!fcmtoken) {
    try {
      fcmtoken = await messaging().getToken();
      if (fcmtoken) {
        await AsyncStorage.setItem('fcmtoken', fcmtoken);
      }
    } catch (error) {
      console.error('[ERROR]', error);
    }
  }

  await updateToken(fcmtoken);
};

const updateToken = async (token) => {
  const user_id = store.getState().user.id;

  if (!user_id && !token) {
    return;
  }

  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-project-token': SOCKET_PROJECT_TOKEN },
    body: JSON.stringify({ token, user_id }),
  };

  try {
    fetch(URL + '/api/v1/fcm/update', requestOptions).then((response) => {
      console.log('Post created at : ', response);
    });
  } catch (error) {
    console.error(error);
  }
};

export const notificationListener = () => {
  return messaging().onMessage(async (remoteMessage) => {
    console.log('A new FCM message arrived!', JSON.stringify(remoteMessage));

    const newNotification = {
      id: 1,
      messageId: remoteMessage.messageId,
      title: remoteMessage.notification.title,
      message: remoteMessage.notification.body,
      channelId: LOCAL_CHANNEL_ID,
      picture: remoteMessage.data.picture,
      largeIconUrl: remoteMessage.data.large_icon_url,
      bigLargeIconUrl: remoteMessage.data.big_large_icon_url,
    };

    PushNotification.localNotification(newNotification);
  });
};

export const setBackgroundMessageHandler = () => {
  messaging().setBackgroundMessageHandler(async (remoteMessage) => {
    console.log('Message handled in the background!', remoteMessage);
  });
};

export const createNotificationChannels = () => {
  PushNotification.createChannel(
    {
      channelId: LOCAL_CHANNEL_ID,
      channelName: LOCAL_CHANNEL_ID,
      channelDescription: 'Channel for local pushes',
      playSound: true,
      soundName: 'default',
      vibrate: true,
    },
    (created) => created
  );
};

export const configurePushNotification = () => {
  PushNotification.configure({
    // (optional) Called when Token is generated (iOS and Android)
    onRegister: function (token) {
      console.log('TOKEN:', token);
    },

    // (required) Called when a remote is received or opened, or local notification is opened
    onNotification: function (notification) {
      console.log('NOTIFICATION:', notification);

      // process the notification

      // (required) Called when a remote is received or opened, or local notification is opened
      //   notification.finish(PushNotificationIOS.FetchResult.NoData);
    },

    // (optional) Called when Registered Action is pressed and invokeApp is false, if true onNotification will be called (Android)
    onAction: function (notification) {
      console.log('ACTION:', notification.action);
      console.log('NOTIFICATION:', notification);

      // process the action
    },

    // (optional) Called when the user fails to register for remote notifications. Typically occurs when APNS is having issues, or the device is a simulator. (iOS)
    onRegistrationError: function (err) {
      console.error(err.message, err);
    },

    // IOS ONLY (optional): default: all - Permissions to register.
    permissions: {
      alert: true,
      badge: true,
      sound: true,
    },

    // Should the initial notification be popped automatically
    // default: true
    popInitialNotification: true,

    /**
     * (optional) default: true
     * - Specified if permissions (ios) and token (android and ios) will requested or not,
     * - if not, you must call PushNotificationsHandler.requestPermissions() later
     * - if you are not using remote notification or do not have Firebase installed, use this:
     *     requestPermissions: Platform.OS === 'ios'
     */
    requestPermissions: true,
  });
};
