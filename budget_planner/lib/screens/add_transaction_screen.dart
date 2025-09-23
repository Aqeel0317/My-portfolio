
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:datetime_picker_formfield/datetime_picker_formfield.dart';
import 'package:intl/intl.dart';
import '../providers/transaction_provider.dart';
import '../models/transaction.dart';
import '../utils/responsive.dart';

class AddTransactionScreen extends StatefulWidget {
  final Transaction? transaction;

  AddTransactionScreen({this.transaction});

  @override
  _AddTransactionScreenState createState() => _AddTransactionScreenState();
}

class _AddTransactionScreenState extends State<AddTransactionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _titleController = TextEditingController();
  final _amountController = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  String _selectedCategory = 'Food';
  bool _isIncome = false;

  final List<String> _categories = [
    'Food', 'Transport', 'Shopping', 
    'Entertainment', 'Utilities', 'Other'
  ];

  @override
  void initState() {
    super.initState();
    if (widget.transaction != null) {
      _titleController.text = widget.transaction!.title;
      _amountController.text = widget.transaction!.amount.toString();
      _selectedDate = widget.transaction!.date;
      _selectedCategory = widget.transaction!.category;
      _isIncome = widget.transaction!.isIncome;
    }
  }

  @override
  Widget build(BuildContext context) {
    final responsive = Responsive(context);
    
    return Scaffold(
      appBar: AppBar(title: Text(widget.transaction == null ? 'Add Transaction' : 'Edit Transaction')),
      body: SingleChildScrollView(
        padding: EdgeInsets.symmetric(
          horizontal: responsive.responsiveValue(mobile: 16, tablet: 32),
          vertical: 16,
        ),
        child: ConstrainedBox(
          constraints: BoxConstraints(
            minHeight: responsive.height - kToolbarHeight,
          ),
          child: IntrinsicHeight(
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  TextFormField(
                    controller: _titleController,
                    decoration: InputDecoration(labelText: 'Title'),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter title';
                      }
                      return null;
                    },
                  ),
                  SizedBox(height: responsive.responsiveValue(mobile: 12, tablet: 16)),
                  
                  TextFormField(
                    controller: _amountController,
                    decoration: InputDecoration(labelText: 'Amount'),
                    keyboardType: TextInputType.number,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter amount';
                      }
                      if (double.tryParse(value) == null) {
                        return 'Please enter valid number';
                      }
                      return null;
                    },
                  ),
                  SizedBox(height: responsive.responsiveValue(mobile: 12, tablet: 16)),
                  
                  DateTimeField(
                    format: DateFormat.yMd(),
                    initialValue: _selectedDate,
                    decoration: InputDecoration(
                      labelText: 'Date',
                      suffixIcon: Icon(Icons.calendar_today),
                    ),
                    onChanged: (dt) => setState(() => _selectedDate = dt!),
                    onShowPicker: (context, currentValue) {
                      return showDatePicker(
                        context: context,
                        firstDate: DateTime(2000),
                        initialDate: currentValue ?? DateTime.now(),
                        lastDate: DateTime(2101),
                      );
                    },
                  ),
                  SizedBox(height: responsive.responsiveValue(mobile: 12, tablet: 16)),
                  
                  DropdownButtonFormField(
                    value: _selectedCategory,
                    items: _categories.map((cat) {
                      return DropdownMenuItem(
                        value: cat,
                        child: Text(cat),
                      );
                    }).toList(),
                    onChanged: (value) => setState(() => _selectedCategory = value.toString()),
                    decoration: InputDecoration(labelText: 'Category'),
                  ),
                  SizedBox(height: responsive.responsiveValue(mobile: 12, tablet: 16)),
                  
                  SwitchListTile(
                    title: Text('Income?'),
                    value: _isIncome,
                    onChanged: (val) => setState(() => _isIncome = val),
                  ),
                  SizedBox(height: responsive.responsiveValue(mobile: 24, tablet: 32)),
                  
                  ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(
                        vertical: responsive.responsiveValue(mobile: 12, tablet: 16),
                      ),
                    ),
                    onPressed: _submitForm,
                    child: Text(widget.transaction == null ? 'Add Transaction' : 'Update Transaction'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _submitForm() {
    if (_formKey.currentState!.validate()) {
      final newTransaction = Transaction(
        id: widget.transaction?.id,
        title: _titleController.text,
        amount: double.parse(_amountController.text),
        isIncome: _isIncome,
        category: _selectedCategory,
        date: _selectedDate,
      );

      if (widget.transaction == null) {
        Provider.of<TransactionProvider>(context, listen: false)
          .addTransaction(newTransaction)
          .then((_) => Navigator.pop(context));
      } else {
        Provider.of<TransactionProvider>(context, listen: false)
          .updateTransaction(newTransaction)
          .then((_) => Navigator.pop(context));
      }
    }
  }
}