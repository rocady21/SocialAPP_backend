"""cambios

Revision ID: bcb04f45189f
Revises: 
Create Date: 2024-01-05 13:44:56.902758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bcb04f45189f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('estado',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('insignia',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=70), nullable=False),
    sa.Column('tipo', sa.String(length=100), nullable=False),
    sa.Column('img', sa.String(length=70), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nombre', sa.String(length=70), nullable=False),
    sa.Column('apellido', sa.String(length=100), nullable=False),
    sa.Column('edad', sa.Integer(), nullable=False),
    sa.Column('presentacion', sa.String(length=100), nullable=True),
    sa.Column('correo', sa.String(length=100), nullable=True),
    sa.Column('contraseña', sa.String(length=200), nullable=False),
    sa.Column('foto', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('correo')
    )
    op.create_table('chat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user_from', sa.Integer(), nullable=False),
    sa.Column('id_user_to', sa.Integer(), nullable=False),
    sa.Column('fecha_inicio', sa.String(length=50), nullable=False),
    sa.Column('last_message', sa.String(length=50), nullable=False),
    sa.Column('id_user_last_message', sa.Integer(), nullable=True),
    sa.Column('date_last_message', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id_user_from'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_user_last_message'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_user_to'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=500), nullable=True),
    sa.Column('fecha', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('seguidor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user_seguidor', sa.Integer(), nullable=False),
    sa.Column('id_usuario_seguido', sa.Integer(), nullable=False),
    sa.Column('fecha_inicio', sa.String(length=100), nullable=False),
    sa.Column('id_estado', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_estado'], ['estado.id'], ),
    sa.ForeignKeyConstraint(['id_user_seguidor'], ['user.id'], ),
    sa.ForeignKeyConstraint(['id_usuario_seguido'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user__insignia',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('id_insignia', sa.Integer(), nullable=False),
    sa.Column('fecha_obt', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['id_insignia'], ['insignia.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comentario__post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('id_post', sa.Integer(), nullable=False),
    sa.Column('comentario', sa.String(length=1000), nullable=False),
    sa.Column('fecha_comentario', sa.String(length=1000), nullable=False),
    sa.ForeignKeyConstraint(['id_post'], ['post.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('like__post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('id_post', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_post'], ['post.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mensajes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_chat', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.String(length=50), nullable=False),
    sa.Column('mensaje', sa.String(length=1000), nullable=False),
    sa.ForeignKeyConstraint(['id_chat'], ['chat.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('photo_post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_post', sa.Integer(), nullable=False),
    sa.Column('photo_url', sa.String(length=1000), nullable=False),
    sa.ForeignKeyConstraint(['id_post'], ['post.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('photo_post')
    op.drop_table('mensajes')
    op.drop_table('like__post')
    op.drop_table('comentario__post')
    op.drop_table('user__insignia')
    op.drop_table('seguidor')
    op.drop_table('post')
    op.drop_table('chat')
    op.drop_table('user')
    op.drop_table('insignia')
    op.drop_table('estado')
    # ### end Alembic commands ###