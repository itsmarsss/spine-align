import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:mobile_scanner/mobile_scanner.dart';

class QRScannerScreen extends StatefulWidget {
  const QRScannerScreen({super.key});

  @override
  State<QRScannerScreen> createState() => _QRScannerScreenState();
}

class _QRScannerScreenState extends State<QRScannerScreen> {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            height: 300.0,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32.0),
              child: MobileScanner(
                onDetect: (barcode) {
                  print("${dotenv.env["BASE_URL"]}/${barcode.barcodes.firstOrNull?.rawValue}");
                },
              ),
            ),
          ),
          const SizedBox(height: 12.0),
          Text("Scan your QR code!", style: Theme.of(context).textTheme.bodyLarge),
          const SizedBox(height: 48.0),
        ],
      ),
    );
  }
}
