import 'package:flutter/material.dart';
import '../database/database_helper.dart';
import '../models/transaction.dart';

class TransactionProvider with ChangeNotifier {
  List<Transaction> _transactions = [];
  Map<String, double> _budgets = {};

  List<Transaction> get transactions => _transactions;
  Map<String, double> get budgets => _budgets;

  Future<void> loadTransactions() async {
    final data = await DatabaseHelper.instance.getTransactions();
    _transactions = data.map((e) => Transaction(
      id: e['id'],
      title: e['title'],
      amount: e['amount'],
      isIncome: e['type'] == 1,
      category: e['category'],
      date: DateTime.parse(e['date']),
    )).toList();
    notifyListeners();
  }

  Future<void> addTransaction(Transaction transaction) async {
    await DatabaseHelper.instance.insertTransaction(transaction.toMap());
    await loadTransactions();
  }

  Future<void> updateTransaction(Transaction transaction) async {
    await DatabaseHelper.instance.updateTransaction(transaction.toMap());
    await loadTransactions();
  }

  Future<void> deleteTransaction(int id) async {
    await DatabaseHelper.instance.deleteTransaction(id);
    await loadTransactions();
  }

  Future<void> loadBudgets() async {
    _budgets = await DatabaseHelper.instance.getBudgets();
    notifyListeners();
  }

  Future<void> setBudget(String category, double amount) async {
    await DatabaseHelper.instance.setBudget({
      'category': category,
      'amount': amount
    });
    await loadBudgets();
  }
}