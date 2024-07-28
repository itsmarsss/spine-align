import 'dart:async';
import 'package:socket_io_client/socket_io_client.dart' as io;
import 'package:flutter/material.dart';
import 'package:flutter_background_service/flutter_background_service.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:mobile/screens/qr_scanner_screen.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:http/http.dart' as http;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  await initializeService();
  runApp(const MyApp());
}

Future<http.Response> fetch(String uri) {
  return http.get(Uri.parse(uri));
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
  final socket = io.io("your-server-url", <String, dynamic>{
    'transports': ['websocket'],
    'autoConnect': true,
  });
  socket.onConnect((_) {
    print('Connected. Socket ID: ${socket.id}');
    // Implement your socket logic here
    // For example, you can listen for events or send data
  });

  socket.onDisconnect((_) {
    print('Disconnected');
  });
  socket.on("event-name", (data) {
    //do something here like pushing a notification
  });
  service.on("stop").listen((event) {
    service.stopSelf();
    print("background process is now stopped");
  });

  service.on("start").listen((event) {});

  Timer.periodic(const Duration(seconds: 1), (timer) {
    socket.emit("event-name", "your-message");
    print("service is successfully running ${DateTime.now().second}");
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
