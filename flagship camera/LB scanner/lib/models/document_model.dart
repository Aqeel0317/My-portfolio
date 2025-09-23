import 'dart:io';

class ScannedDocument {
  final String id;
  final String imagePath;
  final DateTime createdAt;
  String? editedImagePath;

  ScannedDocument({
    required this.id,
    required this.imagePath,
    required this.createdAt,
    this.editedImagePath,
  });

  String get displayPath => editedImagePath ?? imagePath;
  
  Future<bool> get exists async {
    return await File(displayPath).exists();
  }
}

class DocumentSession {
  final String id;
  final List<ScannedDocument> pages;
  final DateTime createdAt;
  String? pdfPath;

  DocumentSession({
    required this.id,
    required this.pages,
    required this.createdAt,
    this.pdfPath,
  });
}