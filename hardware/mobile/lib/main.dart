import 'dart:async';
import 'dart:io';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/material.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile/screens/qr_scanner_screen.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

final storage = FlutterSecureStorage();

final flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
late final InitializationSettings initializationSettings;

initializePlatformSpecifics() async {
  var initializationSettingsAndroid =
      const AndroidInitializationSettings('@mipmap/ic_launcher');
  var initializationSettingsIOS = DarwinInitializationSettings(
    requestAlertPermission: true,
    requestBadgePermission: true,
    requestSoundPermission: false,
    onDidReceiveLocalNotification: (id, title, body, payload) async {
      // your call back to the UI
    },
  );
  initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid, iOS: initializationSettingsIOS);

  await flutterLocalNotificationsPlugin.initialize(initializationSettings);
  // your call back to the UI
}

Future<void> showNotification(String title, String body) async {
  var androidChannelSpecifics = const AndroidNotificationDetails(
    'CHANNEL_ID',
    'CHANNEL_NAME',
    channelDescription: "CHANNEL_DESCRIPTION",
    importance: Importance.max,
    priority: Priority.high,
    icon: '@mipmap/ic_launcher',
    playSound: true,
    timeoutAfter: 5000,
    styleInformation: DefaultStyleInformation(true, true),
  );
  var iosChannelSpecifics = const DarwinNotificationDetails();
  var platformChannelSpecifics = NotificationDetails(
      android: androidChannelSpecifics, iOS: iosChannelSpecifics);
  await flutterLocalNotificationsPlugin.show(
    0, // Notification ID
    title, // Notification Title
    body, // Notification Body, set as null to remove the body
    platformChannelSpecifics, // Notification Payload
  );
}

_requestIOSPermission() {
  flutterLocalNotificationsPlugin
      .resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>()
      ?.requestPermissions(
        alert: false,
        badge: true,
        sound: true,
      );
}

// Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
//   await Firebase.initializeApp();
//   FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
//       FlutterLocalNotificationsPlugin();

//   const AndroidNotificationDetails androidPlatformChannelSpecifics =
//       AndroidNotificationDetails('your_channel_id', 'your_channel_name',
//           channelDescription: 'your_channel_description',
//           importance: Importance.max,
//           priority: Priority.high,
//           showWhen: false);
//   const NotificationDetails platformChannelSpecifics =
//       NotificationDetails(android: androidPlatformChannelSpecifics);
//   await flutterLocalNotificationsPlugin.show(
//       0, 'Slouch Alert', 'You are slouching!', platformChannelSpecifics,
//       payload: 'item x');
// }

// ...

void main() async {
  await dotenv.load(fileName: ".env");
  WidgetsFlutterBinding.ensureInitialized();

  final options = DefaultFirebaseOptions();
  await options.initialize();

  await Firebase.initializeApp(
      name: "spine-align", options: options.currentPlatform);
  // FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  initializePlatformSpecifics();

  if (Platform.isIOS) {
    _requestIOSPermission();
  }

  // FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
  // const AndroidInitializationSettings initializationSettingsAndroid =
  //     AndroidInitializationSettings('@mipmap/ic_launcher');
  // const InitializationSettings initializationSettings = InitializationSettings(
  //   android: initializationSettingsAndroid,
  // );

  // await flutterLocalNotificationsPlugin.initialize(initializationSettings);
  await initializeService();

  FirebaseMessaging messaging = FirebaseMessaging.instance;

  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    announcement: false,
    badge: true,
    carPlay: false,
    criticalAlert: false,
    provisional: false,
    sound: true,
  );

  print('User granted permission: ${settings.authorizationStatus}');
  runApp(const MyApp());
  //insert uri here
}

Future<void> initializeService() async {
  final service = FlutterBackgroundService();

  await service.configure(
    androidConfiguration: AndroidConfiguration(
      autoStart: true,
      onStart: onStart,
      isForegroundMode: false,
      autoStartOnBoot: true,
    ),
    iosConfiguration: IosConfiguration(
      autoStart: false,
      onForeground: null,
      onBackground: null,
    ),
  );

  //start service on compile
  service.startService();
}

@pragma('vm:entry-point')
void onStart(ServiceInstance service) async {
  final options = DefaultFirebaseOptions();
  await options.initialize();

  await Firebase.initializeApp(
      name: "spine-align", options: options.currentPlatform);

  Timer.periodic(const Duration(seconds: 2), (timer) async {
    final qrId = await storage.read(key: "qrId");
    final classId = await storage.read(key: "classId");

    if (qrId == null || classId == null) {
      return;
    }

    print("$qrId $classId");

    final docRef = FirebaseFirestore.instance
        .collection("classes")
        .doc(classId)
        .collection("qrcodes")
        .doc(qrId);
    final docData = await docRef.get();

    if (docData.get("slouching") == true) {
      await showNotification(
          "Watch Out!", "You are slouching. Please sit up straight.");
    }
  });
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'spinealign',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
            seedColor: const Color.fromARGB(255, 71, 68, 217)),
        textTheme: GoogleFonts.lexendTextTheme(),
        useMaterial3: true,
      ),
      home: Scaffold(
        appBar: AppBar(
          title: RichText(
            text: TextSpan(
              style: Theme.of(context).textTheme.headlineLarge,
              children: <TextSpan>[
                const TextSpan(
                  text: "spine",
                ),
                TextSpan(
                  text: "align",
                  style: TextStyle(
                    color: Theme.of(context).primaryColor,
                  ),
                ),
              ],
            ),
          ),
        ),
        body: const QRScannerScreen(),
      ),
    );
  }
}
