import 'dart:async';
import 'dart:io';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:flutter/material.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile/screens/qr_scanner_screen.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;
import 'package:mobile/models/slouch_code.dart';
import 'dart:convert';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'package:firebase_messaging/firebase_messaging.dart';

final flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();
late final InitializationSettings initializationSettings;


initializePlatformSpecifics() {
    var initializationSettingsAndroid =
        const AndroidInitializationSettings('app_notification_icon');
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

    // await flutterLocalNotificationsPlugin.initialize(initializationSettings,
    //     onSelectNotification: (String payload) async {
    //   onNotificationClick(payload);   
 // your call back to the UI

}

Future<void> showNotification(String title, String body) async {
    var androidChannelSpecifics = const AndroidNotificationDetails(
      'CHANNEL_ID',
      'CHANNEL_NAME',
      channelDescription: "CHANNEL_DESCRIPTION",
      importance: Importance.max,
      priority: Priority.high,
      playSound: true,
      timeoutAfter: 5000,
      styleInformation: DefaultStyleInformation(true, true),
    );
    var iosChannelSpecifics = const DarwinNotificationDetails();
    var platformChannelSpecifics =
        NotificationDetails(android: androidChannelSpecifics, iOS: iosChannelSpecifics);
    await flutterLocalNotificationsPlugin.show(
      0,  // Notification ID
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

 

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin = FlutterLocalNotificationsPlugin();

  const AndroidNotificationDetails androidPlatformChannelSpecifics =
      AndroidNotificationDetails('your_channel_id', 'your_channel_name',
          channelDescription: 'your_channel_description',
          importance: Importance.max,
          priority: Priority.high,
          showWhen: false);
  const NotificationDetails platformChannelSpecifics =
      NotificationDetails(android: androidPlatformChannelSpecifics);
  await flutterLocalNotificationsPlugin.show(
      0, 'Slouch Alert', 'You are slouching!', platformChannelSpecifics,
      payload: 'item x');
}

// ...

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    name: "spine-align",
    options: DefaultFirebaseOptions.currentPlatform,
  );
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

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

  await dotenv.load(fileName: ".env");
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
  // final socket = io.io("http://localhost:5173", <String, dynamic>{
  //   'transports': ['websocket'],
  //   'autoConnect': true,
  // });

  // socket.connect();

  // socket.onConnect((_) {
  //   print('Connected. Socket ID: ${socket.id}');
  //   // Implement your socket logic here
  //   // For example, you can listen for events or send data
  // });

  // socket.onDisconnect((_) {
  //   print('Disconnected');
  // });
  // socket.on("poll", (data) {
  //   print("POLLING");
  //   //do something here like pushing a notification
  //   if (pollUri == null || pollUri!.isEmpty) {
  //     return;
  //   }

  //   fetch(pollUri!);
  // });
  // service.on("stop").listen((event) {
  //   service.stopSelf();
  //   print("background process is now stopped");
  // });

  // service.on("start").listen((event) {});

  // Timer.periodic(const Duration(seconds: 1), (timer) {
  //   socket.emit("poll", "");
  //   print("service is successfully running ${DateTime.now().second}");
  // });

  Firebase.initializeApp(
    name: "spine-align",
    options: DefaultFirebaseOptions.currentPlatform,
  );

  Timer.periodic(const Duration(seconds: 2), (timer) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    final qrId = prefs.getString("qrId");
    final classId = prefs.getString("classId");

    final docRef = FirebaseFirestore.instance.collection("classes").doc(classId).collection("qrcodes").doc(qrId);
    final docData = await docRef.get();

    if (docData.get("slouching") == true) {
      // FirebaseMessaging messaging = FirebaseMessaging.instance;
      // await messaging.subscribeToTopic('slouch_alert');

      // // Send a message to the topic
      // await FirebaseMessaging.instance.sendMessage(
      //   to: '/topics/slouch_alert',
      //   data: {
      //     'title': 'Slouch Alert',
      //     'body': 'You are slouching!',
      //   },
      // );      
      await showNotification("Watch Out!", "You are slouching. Please sit up straight."); 
    }
    // print("http://$pollUri");
    // if (pollUri == null || pollUri.isEmpty) {
    //   return;
    // }

    // final sc = await fetch(pollUri);
    // print(sc);
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
        // This is the theme of your application.
        //
        // TRY THIS: Try running your application with "flutter run". You'll see
        // the application has a purple toolbar. Then, without quitting the app,
        // try changing the seedColor in the colorScheme below to Colors.green
        // and then invoke "hot reload" (save your changes or press the "hot
        // reload" button in a Flutter-supported IDE, or press "r" if you used
        // the command line to start the app).
        //
        // Notice that the counter didn't reset back to zero; the application
        // state is not lost during the reload. To reset the state, use hot
        // restart instead.
        //
        // This works for code too, not just values: Most code changes can be
        // tested with just a hot reload.
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
