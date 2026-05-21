import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# IMPORTANTE: Ajuste as importações do 'app' e 'db' de acordo com a sua estrutura!
# Se você usa o padrão Factory (create_app), instancie o app aqui.
from handlink.ext.db import db
from handlink.models import User, Role, RoleUser, Category, Service, Appointment, City, Address
from app import create_app  # Ou de onde quer que você importe sua instância do Flask

app = create_app()

def run_seed():
    """Script para popular o banco de dados do MVP com dados iniciais."""
    
    with app.app_context():
        print("🧹 Limpando o banco de dados atual...")
        db.drop_all()
        print("🏗️ Criando tabelas novamente...")
        db.create_all()

        # ==========================================
        # 1. CRIANDO PERFIS (ROLES)
        # ==========================================
        print("👥 Criando perfis (Roles)...")
        role_admin = Role(name='Admin', status=True)
        role_prestador = Role(name='Prestador', status=True)
        role_cliente = Role(name='Cliente', status=True)
        
        db.session.add_all([role_admin, role_prestador, role_cliente])
        db.session.commit()

        # ==========================================
        # 2. CRIANDO CATEGORIAS
        # ==========================================
        print("🏷️ Criando categorias de serviços...")
        cat_limpeza = Category(name='Limpeza', desc='Faxinas, limpezas pesadas e organização.')
        cat_manutencao = Category(name='Manutenção', desc='Reparos elétricos, encanamento e montagem.')
        cat_aulas = Category(name='Aulas', desc='Aulas particulares, idiomas e reforço escolar.')
        
        db.session.add_all([cat_limpeza, cat_manutencao, cat_aulas])
        db.session.commit()

        # ==========================================
        # 3. CRIANDO CIDADES
        # ==========================================
        print("🏙️ Criando cidades...")
        city_sp = City(name='São Paulo', state='SP', country='Brasil', region='Sudeste')
        city_rj = City(name='Rio de Janeiro', state='RJ', country='Brasil', region='Sudeste')
        city_vitoria = City(name='Vitória', state='ES', country='Brasil', region='Sudeste')
        
        db.session.add_all([city_sp, city_rj, city_vitoria])
        db.session.commit()

        # ==========================================
        # 4. CRIANDO USUÁRIOS E SEUS ENDEREÇOS
        # ==========================================
        print("👤 Criando usuários de teste...")
        
        # 4.1 Admin (Também é cliente)
        admin = User(name='Chefão Admin', email='admin@handlink.com', cpf='000.000.000-00', password='123')
        # 4.2 Prestadora de Serviços
        prestadora = User(name='Maria Eletricista', email='maria@servicos.com', cpf='111.111.111-11', phone='27999999999', password='123')
        # 4.3 Cliente comum
        cliente = User(name='Carlos Cliente', email='carlos@email.com', cpf='222.222.222-22', phone='11988888888', password='123')
        
        db.session.add_all([admin, prestadora, cliente])
        db.session.commit()

        # Adicionando endereços
        end_maria = Address(road='Rua das Flores', number=123, district='Centro', zipcode='29000-000', user_id=prestadora.id, city_id=city_vitoria.id)
        end_carlos = Address(road='Av Paulista', number=1000, district='Bela Vista', zipcode='01310-100', user_id=cliente.id, city_id=city_sp.id)
        db.session.add_all([end_maria, end_carlos])

        # ==========================================
        # 5. ATRIBUINDO PERFIS AOS USUÁRIOS (RoleUser)
        # ==========================================
        print("🔗 Vinculando perfis aos usuários...")
        
        # Admin
        RoleUser(user=admin, role=role_admin)
        RoleUser(user=admin, role=role_cliente)
        
        # Maria (É Cliente e Prestadora Aprovada)
        RoleUser(user=prestadora, role=role_cliente)
        RoleUser(user=prestadora, role=role_prestador, service_provider_status='Aprovado')
        
        # Carlos (Apenas Cliente)
        RoleUser(user=cliente, role=role_cliente)
        
        db.session.commit()

        # ==========================================
        # 6. CRIANDO SERVIÇOS
        # ==========================================
        print("🛠️ Cadastrando serviços...")
        servico_1 = Service(
            provider_id=prestadora.id,
            category_id=cat_manutencao.id,
            city_id=city_vitoria.id,
            name='Instalação de Chuveiro Elétrico',
            desc='Faço a instalação completa e segura de chuveiros de todas as marcas. Fiação nova se necessário.',
            price=Decimal('150.00')
        )
        
        servico_2 = Service(
            provider_id=prestadora.id,
            category_id=cat_manutencao.id,
            city_id=city_vitoria.id,
            name='Troca de Tomadas e Disjuntores',
            desc='Manutenção elétrica residencial rápida e sem sujeira.',
            price=Decimal('80.00')
        )
        
        db.session.add_all([servico_1, servico_2])
        db.session.commit()

        # ==========================================
        # 7. CRIANDO AGENDAMENTOS
        # ==========================================
        print("📅 Gerando agendamentos de teste...")
        
        # Agendamento para amanhã
        data_amanha = datetime.now(timezone.utc) + timedelta(days=1)
        
        agendamento = Appointment(
            client_id=cliente.id,
            service_id=servico_1.id,
            status='Pendente',
            appointment_time=data_amanha
        )
        
        db.session.add(agendamento)
        db.session.commit()

        print("✅ Seed finalizado com sucesso! O banco está pronto para uso.")

if __name__ == '__main__':
    run_seed()