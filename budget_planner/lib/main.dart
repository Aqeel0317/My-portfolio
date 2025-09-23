import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/transaction_provider.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => TransactionProvider(),
      child: MaterialApp(
        title: 'Offline Expense Tracker',
        theme: ThemeData(
          primarySwatch: Colors.indigo,
          visualDensity: VisualDensity.adaptivePlatformDensity,
          textTheme: TextTheme(
            titleLarge: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold),
            bodyMedium: TextStyle(fontSize: 16.0),
          ),
        ),
        home: SplashScreen(),
      ),
    );
  }
}