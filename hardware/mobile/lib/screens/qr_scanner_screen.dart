import 'package:flutter/material.dart';
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

  Future<void> _init() async {
    if (await storage.containsKey(key: "qrId") && await storage.containsKey(key: "classId")) {
      _codeScanned = true;
    }

    // HARD CODING QR CODE SCAN
    await storage.write(key: "qrId", value: "0");
    await storage.write(key: "classId", value: "Utq8xmbAenygSivRZ7TO");
    _codeScanned = true;
  }

  @override
  void initState() {
    super.initState();

    _init();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: !_codeScanned
          ? Column(
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
                        final parts =
                            barcode.barcodes.firstOrNull!.rawValue!.split("/");
                        final qrId = parts.last;
                        parts.removeLast();
                        final classId = parts.last;

                        await storage.write(key: "qrId", value: qrId);
                        await storage.write(key: "classId", value: classId);

                        setState(() {
                          _codeScanned = true;
                        });
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 12.0),
                Text(
                  "Scan your QR code!",
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 48.0),
              ],
            )
          : Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  "Code Scanned!",
                  style: Theme.of(context).textTheme.bodyLarge,
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () async {
                    await storage.delete(key: "qrId");
                    await storage.delete(key: "classId");

                    setState(() {
                      _codeScanned = false;
                    });
                  },
                  style: const ButtonStyle(
                    backgroundColor: WidgetStatePropertyAll(
                        Color.fromARGB(255, 71, 68, 217)),
                  ),
                  child: Text(
                    "Leave Class",
                    style: Theme.of(context).textTheme.labelLarge!.copyWith(
                          color: const Color.fromARGB(255, 240, 240, 240),
                        ),
                  ),
                ),
              ],
            ),
    );
  }
}
