import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import '../models/document_model.dart';

class DocumentManager extends ChangeNotifier {
  static final DocumentManager _instance = DocumentManager._internal();
  factory DocumentManager() => _instance;
  DocumentManager._internal();

  DocumentSession? _currentSession;
  final List<DocumentSession> _sessions = [];

  DocumentSession? get currentSession => _currentSession;
  List<DocumentSession> get sessions => _sessions;

  void startNewSession() {
    _currentSession = DocumentSession(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      pages: [],
      createdAt: DateTime.now(),
    );
    notifyListeners();
  }

  void addPage(ScannedDocument document) {
    if (_currentSession == null) {
      startNewSession();
    }
    _currentSession!.pages.add(document);
    notifyListeners();
  }

  void removePage(int index) {
    if (_currentSession != null && index < _currentSession!.pages.length) {
      _currentSession!.pages.removeAt(index);
      notifyListeners();
    }
  }

  void updatePage(int index, String editedPath) {
    if (_currentSession != null && index < _currentSession!.pages.length) {
      _currentSession!.pages[index].editedImagePath = editedPath;
      notifyListeners();
    }
  }

  void saveSession(String pdfPath) {
    if (_currentSession != null && _currentSession!.pages.isNotEmpty) {
      _currentSession!.pdfPath = pdfPath;
      _sessions.add(_currentSession!);
      _currentSession = null;
      notifyListeners();
    }
  }

  void clearCurrentSession() {
    _currentSession = null;
    notifyListeners();
  }

  Future<void> deleteFiles() async {
    // Clean up temporary files
    try {
      final tempDir = await getTemporaryDirectory();
      final files = tempDir.listSync();
      for (var file in files) {
        if (file is File && file.path.contains('scanned_')) {
          await file.delete();
        }
      }
    } catch (e) {
      debugPrint('Error cleaning files: $e');
    }
  }
}