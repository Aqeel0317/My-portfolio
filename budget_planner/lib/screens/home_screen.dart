import 'dart:io';
import 'package:csv/csv.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import 'add_transaction_screen.dart';
import 'all_transactions_screen.dart';
import 'category_screen.dart';
import '../utils/responsive.dart';
import 'transaction_chart_screen.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  DateTime? _startDate;
  DateTime? _endDate;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance!.addPostFrameCallback((_) {
      Provider.of<TransactionProvider>(
        context,
        listen: false,
      ).loadTransactions();
      Provider.of<TransactionProvider>(context, listen: false).loadBudgets();
    });
  }

  @override
  Widget build(BuildContext context) {
    final responsive = Responsive(context);
    final provider = Provider.of<TransactionProvider>(context);

    final filteredTransactions = provider.transactions.where((t) {
      if (_startDate != null && t.date.isBefore(_startDate!)) {
        return false;
      }
      if (_endDate != null && t.date.isAfter(_endDate!)) {
        return false;
      }
      return true;
    }).toList();

    final expenses = filteredTransactions.where((t) => !t.isIncome).toList();

    // Calculate category spending
    Map<String, double> categorySpending = {};
    for (var expense in expenses) {
      categorySpending.update(
        expense.category,
        (value) => value + expense.amount,
        ifAbsent: () => expense.amount,
      );
    }

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.blue.shade800, Colors.blue.shade400],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: CustomScrollView(
          slivers: [
            SliverAppBar(
              title: Text(
                'Expense Tracker',
                style: TextStyle(color: Colors.white),
              ),
              backgroundColor: Colors.transparent,
              elevation: 0,
              actions: [
                IconButton(
                  icon: Icon(Icons.download, color: Colors.white),
                  onPressed: () => _exportToCsv(filteredTransactions),
                ),
                IconButton(
                  icon: Icon(Icons.filter_list, color: Colors.white),
                  onPressed: _showDateRangePicker,
                ),
                IconButton(
                  icon: Icon(Icons.category, color: Colors.white),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => CategoryScreen()),
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.bar_chart, color: Colors.white),
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => TransactionChartScreen()),
                  ),
                ),
              ],
            ),
            SliverToBoxAdapter(
              child: Column(
                children: [
                  // Summary Cards - Responsive layout
                  _buildSummarySection(responsive, provider),

                  SizedBox(
                    height: responsive.responsiveValue(mobile: 16, tablet: 24),
                  ),

                  // Chart section
                  _buildChartSection(responsive, provider, categorySpending),

                  SizedBox(
                    height: responsive.responsiveValue(mobile: 16, tablet: 24),
                  ),

                  // Recent Transactions
                  _buildTransactionsSection(responsive, filteredTransactions),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.add),
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => AddTransactionScreen()),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.blue.shade800,
      ),
    );
  }

  Widget _buildSummarySection(
    Responsive responsive,
    TransactionProvider provider,
  ) {
    final income = provider.transactions
        .where((t) => t.isIncome)
        .fold(0.0, (sum, t) => sum + t.amount);

    final expense = provider.transactions
        .where((t) => !t.isIncome)
        .fold(0.0, (sum, t) => sum + t.amount);

    final balance = income - expense;

    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: responsive.responsiveValue(mobile: 8, tablet: 16),
        vertical: 16,
      ),
      child: responsive.isMobile
          ? Column(
              children: [
                _buildSummaryCard(
                  'Income',
                  income,
                  Colors.green,
                  responsive,
                  icon: Icons.arrow_upward,
                ),
                SizedBox(height: 12),
                _buildSummaryCard(
                  'Expense',
                  expense,
                  Colors.red,
                  responsive,
                  icon: Icons.arrow_downward,
                ),
                SizedBox(height: 12),
                _buildSummaryCard(
                  'Balance',
                  balance,
                  Colors.blue,
                  responsive,
                  icon: Icons.account_balance_wallet,
                ),
              ],
            )
          : Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    'Income',
                    income,
                    Colors.green,
                    responsive,
                    icon: Icons.arrow_upward,
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: _buildSummaryCard(
                    'Expense',
                    expense,
                    Colors.red,
                    responsive,
                    icon: Icons.arrow_downward,
                  ),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: _buildSummaryCard(
                    'Balance',
                    balance,
                    Colors.blue,
                    responsive,
                    icon: Icons.account_balance_wallet,
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildSummaryCard(
    String title,
    double amount,
    Color color,
    Responsive responsive, {
    IconData? icon,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [color.withOpacity(0.7), color],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Padding(
          padding: EdgeInsets.all(
            responsive.responsiveValue(mobile: 12, tablet: 16),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (icon != null)
                    Icon(
                      icon,
                      color: Colors.white,
                      size: responsive.responsiveValue(mobile: 20, tablet: 24),
                    ),
                  if (icon != null) SizedBox(width: 8),
                  Text(
                    title,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: responsive.responsiveValue(
                        mobile: 16,
                        tablet: 18,
                      ),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              SizedBox(height: 8),
              Text(
                '\$${amount.toStringAsFixed(2)}',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: responsive.responsiveValue(mobile: 20, tablet: 24),
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildChartSection(
    Responsive responsive,
    TransactionProvider provider,
    Map<String, double> categorySpending,
  ) {
    return Card(
      margin: EdgeInsets.symmetric(
        horizontal: responsive.responsiveValue(mobile: 8, tablet: 24),
      ),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text(
              'Spending by Category',
              style: TextStyle(
                fontSize: responsive.responsiveValue(mobile: 18, tablet: 22),
                fontWeight: FontWeight.bold,
                color: Colors.blue.shade800,
              ),
            ),
            SizedBox(height: 24),
            Container(
              height: responsive.responsiveValue(mobile: 200, tablet: 300),
              child: PieChart(
                PieChartData(
                  sections: _buildChartSections(
                    categorySpending,
                    provider.budgets,
                  ),
                  centerSpaceRadius: responsive.responsiveValue(
                    mobile: 40,
                    tablet: 60,
                  ),
                  sectionsSpace: 2,
                ),
              ),
            ),
            SizedBox(height: 24),
            _buildCategoryLegend(categorySpending, responsive),
          ],
        ),
      ),
    );
  }

  List<PieChartSectionData> _buildChartSections(
    Map<String, double> spending,
    Map<String, double> budgets,
  ) {
    return spending.entries.map((entry) {
      final budget = budgets[entry.key] ?? 0;
      final percentage = budget > 0 ? (entry.value / budget) * 100 : 0;

      return PieChartSectionData(
        color: _getCategoryColor(entry.key),
        value: entry.value,
        title: '${percentage.toStringAsFixed(1)}%',
        radius: 20,
        titleStyle: TextStyle(fontSize: 12, color: Colors.white),
      );
    }).toList();
  }

  Widget _buildCategoryLegend(
    Map<String, double> spending,
    Responsive responsive,
  ) {
    return Wrap(
      spacing: responsive.responsiveValue(mobile: 8, tablet: 16),
      runSpacing: responsive.responsiveValue(mobile: 4, tablet: 8),
      alignment: WrapAlignment.center,
      children: spending.entries.map((entry) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 12,
              height: 12,
              color: _getCategoryColor(entry.key),
            ),
            SizedBox(width: 4),
            Text(
              entry.key,
              style: TextStyle(
                fontSize: responsive.responsiveValue(mobile: 12, tablet: 14),
              ),
            ),
          ],
        );
      }).toList(),
    );
  }

  Widget _buildTransactionsSection(
    Responsive responsive,
    List<Transaction> transactions,
  ) {
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: responsive.responsiveValue(mobile: 8, tablet: 24),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Recent Transactions',
            style: TextStyle(
              fontSize: responsive.responsiveValue(mobile: 16, tablet: 20),
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 12),
          ...transactions
              .take(10)
              .map(
                (transaction) => _buildTransactionTile(transaction, responsive),
              )
              .toList(),
          if (transactions.length > 10)
            TextButton(
              onPressed: () => _viewAllTransactions(context, transactions),
              child: Text('View All'),
            ),
        ],
      ),
    );
  }

  Widget _buildTransactionTile(Transaction transaction, Responsive responsive) {
    return Card(
      margin: EdgeInsets.only(bottom: 8),
      child: ListTile(
        contentPadding: EdgeInsets.symmetric(
          horizontal: responsive.responsiveValue(mobile: 12, tablet: 16),
          vertical: responsive.responsiveValue(mobile: 4, tablet: 8),
        ),
        leading: CircleAvatar(
          backgroundColor: _getCategoryColor(
            transaction.category,
          ).withOpacity(0.2),
          child: Icon(
            _getCategoryIcon(transaction.category),
            color: _getCategoryColor(transaction.category),
          ),
        ),
        title: Text(
          transaction.title,
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(DateFormat('MMM dd, yyyy').format(transaction.date)),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${transaction.isIncome ? '+' : '-'} \$${transaction.amount.toStringAsFixed(2)}',
              style: TextStyle(
                fontSize: responsive.responsiveValue(mobile: 14, tablet: 16),
                fontWeight: FontWeight.bold,
                color: transaction.isIncome ? Colors.green : Colors.red,
              ),
            ),
            IconButton(
              icon: Icon(Icons.edit),
              onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) =>
                      AddTransactionScreen(transaction: transaction),
                ),
              ),
            ),
            IconButton(
              icon: Icon(Icons.delete),
              onPressed: () => Provider.of<TransactionProvider>(
                context,
                listen: false,
              ).deleteTransaction(transaction.id!),
            ),
          ],
        ),
      ),
    );
  }

  // Helper to get icon for category
  IconData _getCategoryIcon(String category) {
    switch (category) {
      case 'Food':
        return Icons.restaurant;
      case 'Transport':
        return Icons.directions_car;
      case 'Shopping':
        return Icons.shopping_bag;
      case 'Entertainment':
        return Icons.movie;
      case 'Utilities':
        return Icons.bolt;
      default:
        return Icons.category;
    }
  }

  Color _getCategoryColor(String category) {
    final colors = [
      Colors.blue,
      Colors.red,
      Colors.green,
      Colors.orange,
      Colors.purple,
      Colors.teal,
    ];
    return colors[category.hashCode % colors.length];
  }

  void _viewAllTransactions(
    BuildContext context,
    List<Transaction> transactions,
  ) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AllTransactionsScreen(transactions: transactions),
      ),
    );
  }

  Future<void> _exportToCsv(List<Transaction> transactions) async {
    List<List<dynamic>> rows = [];
    rows.add(['ID', 'Title', 'Amount', 'Type', 'Category', 'Date']);
    for (var transaction in transactions) {
      rows.add([
        transaction.id,
        transaction.title,
        transaction.amount,
        transaction.isIncome ? 'Income' : 'Expense',
        transaction.category,
        DateFormat('yyyy-MM-dd').format(transaction.date),
      ]);
    }

    final directory = await getApplicationDocumentsDirectory();
    final path = '${directory.path}/transactions.csv';
    final file = File(path);
    String csv = const ListToCsvConverter().convert(rows);
    await file.writeAsString(csv);

    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('CSV file saved to $path')));
  }

  Future<void> _showDateRangePicker() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2000),
      lastDate: DateTime.now().add(Duration(days: 365)),
      initialDateRange: _startDate != null && _endDate != null
          ? DateTimeRange(start: _startDate!, end: _endDate!)
          : null,
    );
    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
    }
  }
}
