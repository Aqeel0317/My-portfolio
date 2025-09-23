import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';

class TransactionChartScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<TransactionProvider>(context);
    final transactions = provider.transactions;

    return Scaffold(
      appBar: AppBar(title: Text('Transaction History')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: BarChart(
          BarChartData(
            alignment: BarChartAlignment.spaceAround,
            maxY: _calculateMaxY(transactions),
            barGroups: _createBarGroups(transactions),
            titlesData: FlTitlesData(
              leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true)),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  getTitlesWidget: (double value, TitleMeta meta) {
                    final text = DateFormat('dd').format(
                      DateTime.now().subtract(Duration(days: value.toInt())),
                    );
                    return SideTitleWidget(
                      axisSide: meta.axisSide,
                      space: 16,
                      child: Text(
                        text,
                        style: const TextStyle(
                          color: Color(0xff7589a2),
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                    );
                  },
                  reservedSize: 42,
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  double _calculateMaxY(List<Transaction> transactions) {
    if (transactions.isEmpty) {
      return 0;
    }
    return transactions.map((t) => t.amount).reduce((a, b) => a > b ? a : b);
  }

  List<BarChartGroupData> _createBarGroups(List<Transaction> transactions) {
    Map<int, double> dailyTotals = {};
    for (var tx in transactions) {
      dailyTotals.update(
        tx.date.day,
        (value) => value + tx.amount,
        ifAbsent: () => tx.amount,
      );
    }

    return dailyTotals.entries.map((entry) {
      return BarChartGroupData(
        x: entry.key,
        barRods: [
          BarChartRodData(toY: entry.value, color: Colors.lightBlueAccent),
        ],
      );
    }).toList();
  }
}
