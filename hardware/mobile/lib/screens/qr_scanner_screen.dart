import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:mobile/main.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:shared_preferences/shared_preferences.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {

  bool _codeScanned = false;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: !_codeScanned ? Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            height: 300.0,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: MobileScanner(
                onDetect: (barcode) async {
                  final parts = barcode.barcodes.firstOrNull!.rawValue!.split("/");
                  final qrId = parts.last;
                  parts.removeLast();
                  final classId = parts.last;

                  final prefs = await SharedPreferences.getInstance();

                  prefs.setString("qrId", qrId);
                  prefs.setString("classId", classId);

                  setState(() {
                    _codeScanned = true;
                  }); 




                  
                },
              ),
            ),
          ),
          const SizedBox(height: 12.0),
          Text("Scan your QR code!", style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 48.0),
        ],
      ) : const Text("Code Scanned!"),
    );
  }
}
