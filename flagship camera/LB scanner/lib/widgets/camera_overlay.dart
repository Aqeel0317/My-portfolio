import 'package:flutter/material.dart';

class CameraOverlay extends StatelessWidget {
  const CameraOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: OverlayPainter(),
      child: Container(),
    );
  }
}

class OverlayPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.black.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    final rect = Rect.fromLTWH(0, 0, size.width, size.height);
    final documentRect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: size.width * 0.85,
      height: size.height * 0.6,
    );

    // Draw overlay
    final path = Path()
      ..addRect(rect)
      ..addRRect(RRect.fromRectAndRadius(
        documentRect,
        const Radius.circular(20),
      ))
      ..fillType = PathFillType.evenOdd;

    canvas.drawPath(path, paint);

    // Draw corner markers
    final cornerPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.0;

    const cornerLength = 30.0;
    
    // Top-left corner
    canvas.drawLine(
      Offset(documentRect.left, documentRect.top + cornerLength),
      Offset(documentRect.left, documentRect.top),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(documentRect.left, documentRect.top),
      Offset(documentRect.left + cornerLength, documentRect.top),
      cornerPaint,
    );

    // Top-right corner
    canvas.drawLine(
      Offset(documentRect.right - cornerLength, documentRect.top),
      Offset(documentRect.right, documentRect.top),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(documentRect.right, documentRect.top),
      Offset(documentRect.right, documentRect.top + cornerLength),
      cornerPaint,
    );

    // Bottom-left corner
    canvas.drawLine(
      Offset(documentRect.left, documentRect.bottom - cornerLength),
      Offset(documentRect.left, documentRect.bottom),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(documentRect.left, documentRect.bottom),
      Offset(documentRect.left + cornerLength, documentRect.bottom),
      cornerPaint,
    );

    // Bottom-right corner
    canvas.drawLine(
      Offset(documentRect.right - cornerLength, documentRect.bottom),
      Offset(documentRect.right, documentRect.bottom),
      cornerPaint,
    );
    canvas.drawLine(
      Offset(documentRect.right, documentRect.bottom),
      Offset(documentRect.right, documentRect.bottom - cornerLength),
      cornerPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}