

def build_report(rep_name: str, rep_format: str, **kwargs):
    """
    
    """
    
    buffer = None
    
    if rep_name == 'SOFIERS':
        
        from report_sofier import report_sofier
        buffer = report_sofier(**kwargs)
        
    elif rep_name == 'SALDOS':
        
        from report_balance import report_balance
        buffer = report_balance(**kwargs)
        
    elif rep_name == 'EXTRATO':
        
        from report_statement import report_statement
        buffer = report_statement(**kwargs)
        
    elif rep_name == 'RESERVADOS':
        
        from report_reserveds import get_reserveds
        buffer = get_reserveds(**kwargs)
    
    else:
        
        raise Exception(f'O relatório [{rep_name}] e/ou o formato [{rep_format}] não foram previstos')
        
    if rep_format == 'CSV':
        from to_csv import to_csv
        final_result = to_csv(*buffer)
        
    elif rep_format == 'JSON':
        final_result = {'data': buffer[1]}
        
    return final_result