import discord
import asyncio
from sqlalchemy.orm import sessionmaker
from data.db_setup import engine, Filme
import requests
from config.config import TMDB_API_KEY
from datetime import datetime, timedelta
import random

Session = sessionmaker(bind=engine)
session = Session()

def setup(bot):
    @bot.command()
    async def addfilme(ctx, *, filme: str):
        filme = filme.strip()
        adicionado_por = str(ctx.author.id)
        server_id = str(ctx.guild.id)  
  
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={filme}&language=pt-BR"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                  
                    movie = results[0]
                    movie_id = movie.get('id')
                    title_pt = movie.get('title')
                    title_original = movie.get('original_title')
                    release_date = movie.get('release_date')
                    rating = movie.get('vote_average')
                    poster_path = movie.get('poster_path')

                 
                    existe_filme = session.query(Filme).filter(
                        (Filme.filme == title_pt) | (Filme.titulo_original == title_original) & (Filme.server_id == server_id)
                    ).first()

                    if existe_filme:
                        await ctx.send(f'O filme "{title_pt}" já existe na lista.')
                    else:
                     
                        formatted_date = "Data não disponível"
                        if release_date:
                            formatted_date = datetime.strptime(release_date, '%Y-%m-%d').strftime('%d/%m/%Y')
                        
                     
                        movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
                        details_response = requests.get(movie_details_url, timeout=5)
                        
                        if details_response.status_code == 200:
                            details_data = details_response.json()
                            duration = details_data.get('runtime')
                            genres = details_data.get('genres', [])
                            genre_names = ', '.join(genre['name'] for genre in genres) if genres else "Gênero não disponível" 
                            description = details_data.get('overview', "Descrição não disponível")
                        else:
                            duration = None
                            description = "Descrição não disponível"
                        
                    
                        novo_filme = Filme(
                            filme=title_pt,
                            titulo_original=title_original,
                            genero=genre_names,
                            descricao=description,
                            data_lancamento=formatted_date,
                            avaliacao=rating,
                            duracao=duration,
                            imagem=poster_path,
                            adicionado_por=adicionado_por,
                            server_id=server_id
                        )
                        
                  
                        session.add(novo_filme)
                        session.commit()
                        
                 
                        embed = discord.Embed(
                        title=f"🎬 Filme Adicionado: \n {title_pt}",
                        color=discord.Color.green()
                        )
                        embed.add_field(name="Título Original", value=title_original, inline=False)
                        embed.add_field(name="Lançamento", value=formatted_date, inline=False)
                        embed.add_field(name="Gênero", value=genre_names, inline=False)
                        embed.add_field(name="Avaliação", value=f"{rating}/10", inline=False)
                        embed.add_field(name="Duração", value=f"{duration} minutos" if duration else "Duração não disponível", inline=False)
                        embed.add_field(name="Descrição", value=description, inline=False)
                        embed.set_footer(text=f"Adicionado por: {ctx.author.name}", icon_url=ctx.author.display_avatar)

                        if poster_path:
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                            embed.set_image(url=poster_url)
                        
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("Nenhum filme encontrado com esse título.")
            elif response.status_code == 401:
                await ctx.send("Erro 401: Não autorizado. Verifique sua chave da API TMDB.")
            else:
                error_message = f"Ocorreu um erro ao acessar a API do TMDB: {response.status_code} - {response.reason}"
                await ctx.send(error_message)
        
        except requests.Timeout:
            await ctx.send("A busca demorou demais e não foi possível obter os dados.")
        except requests.RequestException as e:
            await ctx.send(f"Ocorreu um erro ao acessar a API do TMDB: {str(e)}")

    @bot.command()
    async def listafilmes(ctx):
        server_id = str(ctx.guild.id)  
        filmes = session.query(Filme).filter_by(server_id=server_id).all()  

        if not filmes:
            await ctx.send("Não há filmes cadastrados para este servidor.")
            return

       
        current_page = 0
        total_pages = len(filmes)

      
        def create_embed(page):
            embed = discord.Embed(
                title="🎬 Lista de Filmes",
                color=discord.Color.blue()
            )

            filme = filmes[page]  

            movie_info = (
                f"**Título:** {filme.filme}\n"
                f"**Título Original:** {filme.titulo_original}\n"
                f"**Gênero:** {filme.genero}\n"
                f"**Lançamento:** {filme.data_lancamento}\n"
                f"**Avaliação:** {filme.avaliacao}/10\n"
                f"**Duração:** {filme.duracao} minutos\n"
                f"**Descrição:** {filme.descricao}\n"
                f"**Adicionado por:** <@{filme.adicionado_por}>\n"
            )
            embed.add_field(name="Filme", value=movie_info, inline=False)

            if filme.imagem:
                poster_url = f"https://image.tmdb.org/t/p/w500{filme.imagem}"
                embed.set_image(url=poster_url) 

            embed.set_footer(text=f"Página {page + 1}/{total_pages}") 
            return embed


        message = await ctx.send(embed=create_embed(current_page))
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")

      
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction, user) 

                if str(reaction.emoji) == "▶️":
                    if current_page < total_pages - 1:
                        current_page += 1
                        await message.edit(embed=create_embed(current_page))
                elif str(reaction.emoji) == "◀️":
                    if current_page > 0:
                        current_page -= 1
                        await message.edit(embed=create_embed(current_page))
            
            except asyncio.TimeoutError:
                await message.clear_reactions()  
                break



    @bot.command()
    async def removefilme(ctx, *, filme: str):
        filme = filme.strip()
        existe_filme = session.query(Filme).filter_by(filme=filme).first()

        if existe_filme:
          
            embed = discord.Embed(
                title="🎬 Filme a ser removido",
                color=discord.Color.red()
            )

            movie_info = (
                f"**Título:** {existe_filme.filme}\n"
                f"**Título Original:** {existe_filme.titulo_original}\n"
                f"**Gênero:** {existe_filme.genero}\n"
                f"**Lançamento:** {existe_filme.data_lancamento}\n"
                f"**Avaliação:** {existe_filme.avaliacao}/10\n"
                f"**Duração:** {existe_filme.duracao} minutos\n"
                f"**Descrição:** {existe_filme.descricao}\n"  
                f"**Adicionado por:** <@{existe_filme.adicionado_por}>"
            )

            embed.add_field(name="Informações do Filme", value=movie_info, inline=False)

            if existe_filme.imagem:
                poster_url = f"https://image.tmdb.org/t/p/w500{existe_filme.imagem}"
                embed.set_image(url=poster_url)  

            await ctx.send(embed=embed) 

      
            await ctx.send("Você deseja remover este filme? Responda com 'sim' ou 'não'.")

            def check_response(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['sim', 'não']

            try:
                response = await bot.wait_for('message', timeout=30.0, check=check_response)

                if response.content.lower() == 'sim':
                    session.delete(existe_filme)
                    session.commit()  
                    await ctx.send(f'Filme removido: {filme}')
                else:
                    await ctx.send('Remoção cancelada.')

            except asyncio.TimeoutError:
                await ctx.send('Tempo esgotado. Remoção cancelada.')

        else:
            await ctx.send(f'Filme não encontrado na lista: {filme}')
            
    @bot.command()
    async def removefilmeusuario(ctx, user: discord.Member):
        user_id = str(user.id)  

        filmes_do_usuario = session.query(Filme).filter_by(adicionado_por=user_id).all()

        if not filmes_do_usuario:
            await ctx.send(f"O usuário {user.mention} não adicionou nenhum filme.")
            return

       
        embed = discord.Embed(
            title=f"🎬 Filmes de {user.display_name} a serem removidos",
            color=discord.Color.red()
        )

        for filme in filmes_do_usuario:
            movie_info = (
                f"**Título:** {filme.filme}\n"
                f"**Título Original:** {filme.titulo_original}\n"
                f"**Gênero:** {filme.genero}\n"
                f"**Lançamento:** {filme.data_lancamento}\n"
                f"**Avaliação:** {filme.avaliacao}/10\n"
                f"**Duração:** {filme.duracao} minutos\n"
                f"**Descrição:** {filme.descricao}\n"  
            )
            embed.add_field(name=filme.filme, value=movie_info, inline=False)

        
        await ctx.send(embed=embed)

        await ctx.send(f"Você deseja remover todos os filmes de {user.mention}? Responda com 'sim' ou 'não'.")

        def check_response(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['sim', 'não']

        try:
            response = await bot.wait_for('message', timeout=30.0, check=check_response)

            if response.content.lower() == 'sim':
                for filme in filmes_do_usuario:
                    session.delete(filme)

                session.commit() 
                await ctx.send(f"Todos os filmes adicionados por {user.mention} foram removidos.")
            else:
                await ctx.send('Remoção cancelada.')

        except asyncio.TimeoutError:
            await ctx.send('Tempo esgotado. Remoção cancelada.')

    @bot.command()
    async def procurafilme(ctx, *, query: str):
        query = query.strip()

        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=pt-BR"

        try:
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                if results:
                    results = sorted(results, key=lambda x: x.get('popularity', 0), reverse=True)

                    filmes_relevantes = [
                        movie for movie in results
                        if query.lower() in movie['title'].lower() or query.lower() in movie['original_title'].lower()
                    ]

                    if filmes_relevantes:
                        await ctx.send("**Filmes encontrados:**")

                    
                        current_page = 0
                        max_pages = len(filmes_relevantes)
                        

                        def create_embed(page):
                            movie = filmes_relevantes[page]

                            title_pt = movie.get('title', 'Título não disponível')
                            title_original = movie.get('original_title', 'Título original não disponível')
                            release_date = movie.get('release_date', 'Data não disponível')
                            rating = movie.get('vote_average', 'Avaliação não disponível')
                            poster_path = movie.get('poster_path')
                            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                            movie_id = movie.get('id')

                         
                            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
                            details_response = requests.get(details_url, timeout=5)

                            if details_response.status_code == 200:
                                movie_details = details_response.json()
                                runtime = movie_details.get('runtime', 'Duração não disponível')
                                genres = movie_details.get('genres', [])
                                genre_names = ', '.join(genre['name'] for genre in genres) if genres else "Gênero não disponível"
                                description = movie_details.get('overview', 'Descrição não disponível')
                            else:
                                runtime = "Duração não disponível"
                                genre_names = "Gênero não disponível"
                                description = "Descrição não disponível"

                            embed = discord.Embed(
                                title=title_pt,
                                description=description,
                                color=discord.Color.blue()
                            )
                            embed.add_field(name="Título Original", value=title_original, inline=False)
                            embed.add_field(name="Gênero", value=genre_names, inline=False)
                            embed.add_field(name="Data de Lançamento", value=release_date, inline=False)
                            embed.add_field(name="Avaliação", value=f"{rating}/10", inline=True)
                            embed.add_field(name="Duração", value=f"{runtime} minutos", inline=True)

                            if poster_url:
                                embed.set_image(url=poster_url)

                            embed.set_footer(text=f"Página {page + 1}/{max_pages}")
                            return embed

                        embed = create_embed(current_page)
                        message = await ctx.send(embed=embed)

                        await message.add_reaction("⬅️")
                        await message.add_reaction("➡️")

            
                        def check(reaction, user):
                            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"]

                        while True:
                            try:
                                reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

                                if str(reaction.emoji) == "➡️":
                                    if current_page + 1 < max_pages:
                                        current_page += 1
                                        await message.edit(embed=create_embed(current_page))
                                        await message.remove_reaction(reaction.emoji, user)
                                    else:
                                        await message.remove_reaction(reaction.emoji, user)

                                elif str(reaction.emoji) == "⬅️":
                                    if current_page > 0:
                                        current_page -= 1
                                        await message.edit(embed=create_embed(current_page))
                                        await message.remove_reaction(reaction.emoji, user)
                                    else:
                                        await message.remove_reaction(reaction.emoji, user)

                            except TimeoutError:
                                break
                    else:
                        await ctx.send("Nenhum filme encontrado.")
                else:
                    await ctx.send("Nenhum filme encontrado.")
            elif response.status_code == 401:
                await ctx.send("Erro 401: Não autorizado. Verifique sua chave da API TMDB.")
            else:
                error_message = f"Ocorreu um erro ao acessar a API do TMDB: {response.status_code} - {response.reason}"
                await ctx.send(error_message)

        except requests.Timeout:
            await ctx.send("A busca demorou demais e não foi possível obter os dados.")
        except requests.RequestException as e:
            await ctx.send(f"Ocorreu um erro ao acessar a API do TMDB: {str(e)}")


    @bot.command()
    async def geraarquivo(ctx):
        filmes = session.query(Filme).all()

        if filmes:
            conteudo_arquivo = "\n".join([
                f"Título Original: {filme.titulo_original}, Título: {filme.filme}, Lançamento: {filme.data_lancamento}, Avaliação: {filme.avaliacao}/10" 
                for filme in filmes
            ])

            nome_arquivo = "data/files/filmes_indicados.txt"

            try:
                with open(nome_arquivo, 'w', encoding='utf-8') as f:
                    f.write(conteudo_arquivo)

                await ctx.send("Aqui está o arquivo com os títulos originais dos filmes:", file=discord.File(nome_arquivo))
            except Exception as e:
                await ctx.send(f"Ocorreu um erro ao criar o arquivo: {str(e)}")
        else:
            await ctx.send("Não há filmes no banco de dados.")

    @bot.command()
    async def tempofilme(ctx, *, filme: str):
        filme = filme.strip()
        
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={filme}&language=pt-BR"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results:
                    movie = results[0]  
                    movie_id = movie.get('id')
                    title_pt = movie.get('title')
                    
                    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=pt-BR"
                    details_response = requests.get(movie_details_url, timeout=5)
                    
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        duration = details_data.get('runtime')

                        if duration is None:
                            await ctx.send(f'O filme "{title_pt}" não tem uma duração registrada.')
                            return

                        hora_atual = datetime.now()
                        hora_termino = hora_atual + timedelta(minutes=duration)
                        hora_atual_str = hora_atual.strftime('%H:%M')
                        hora_termino_str = hora_termino.strftime('%H:%M')

                     
                        embed = discord.Embed(title=f"Assistindo: {title_pt}", color=0x1abc9c)
                        embed.add_field(name="Início agora", value=hora_atual_str, inline=False)
                        embed.add_field(name="Termina às", value=hora_termino_str, inline=False)
                        embed.add_field(name="Duração", value=f"{duration} minutos", inline=False)
                        embed.set_footer(text="Aproveite o filme!")

                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"Erro ao buscar detalhes do filme: {details_response.status_code} - {details_response.reason}")
                else:
                    await ctx.send(f"Nenhum filme encontrado com o nome '{filme}'.")
            else:
                await ctx.send(f"Erro ao buscar filme: {response.status_code} - {response.reason}")
        
        except requests.Timeout:
            await ctx.send("A busca demorou demais e não foi possível obter os dados.")
        except requests.RequestException as e:
            await ctx.send(f"Ocorreu um erro ao acessar a API do TMDB: {str(e)}")
            
    @bot.command()
    async def limpafilmes(ctx):
        await ctx.send("Tem certeza que deseja remover todos os filmes do banco de dados? Responda com 'sim' para confirmar.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg = await bot.wait_for('message', check=check, timeout=30)  
            if msg.content.lower() == 'sim':
              
                session.query(Filme).delete()
                session.commit()
                await ctx.send("Todos os filmes foram removidos do banco de dados.")
            else:
                await ctx.send("Operação cancelada.")
        except asyncio.TimeoutError:
            await ctx.send("Tempo de espera excedido. Operação cancelada.")
            
    @bot.command()
    async def sorteafilme(ctx):  
        server_id = str(ctx.guild.id)  
        filmes = session.query(Filme).filter_by(server_id=server_id).all()
            
        if not filmes:
            await ctx.send("Não há filmes cadastrados para sortear.")
            return
            
        filme_sorteado = random.choice(filmes)
            
        embed = discord.Embed(title="🎬 Filme Sorteado", color=0x3498db)
        embed.add_field(name="Título", value=filme_sorteado.filme, inline=False)
        embed.add_field(name="Título Original", value=filme_sorteado.titulo_original, inline=False)
        embed.add_field(name="Gênero", value=filme_sorteado.genero, inline=False)
        embed.add_field(name="Lançamento", value=filme_sorteado.data_lancamento, inline=False)
        embed.add_field(name="Avaliação", value=f"{filme_sorteado.avaliacao}/10", inline=False)
        embed.add_field(name="Duração", value=f"{filme_sorteado.duracao} minutos" if filme_sorteado.duracao else "Duração não disponível", inline=False)
        embed.add_field(name="Descrição", value=filme_sorteado.descricao, inline=False)  

        try:
            user_id = int(filme_sorteado.adicionado_por)
            
           
            embed.add_field(name="Adicionado por", value=f"<@{user_id}>", inline=False)
        except ValueError:
            embed.add_field(name="Adicionado por", value="ID de usuário inválido", inline=False)

        if filme_sorteado.imagem:
            poster_url = f"https://image.tmdb.org/t/p/w500{filme_sorteado.imagem}"  
            embed.set_image(url=poster_url)
                    
        await ctx.send(embed=embed)


    @bot.remove_command('help')          
    @bot.command(name='help')
    async def help_command(ctx):
        help_message = (
            "Aqui estão os comandos disponíveis:\n\n"
            "`db!addfilme <nome do filme>` - Adiciona um filme à lista.\n"
            "`db!removefilme <nome do filme>` - Remove um filme da lista.\n"
            "`db!listafilmes` - Exibe todos os filmes na lista.\n"
            "`db!procurafilme <nome do filme>` - Procura um filme na TMDB.\n"
            "`db!geraarquivo` - Gera uma lista dos filmes na lista.\n"
            "`db!tempofilme <nome do filme>` - Informa a hora que o filme acaba.\n"
            "`db!limpafilmes` - Remove todos os filmes da lista.\n"
            "`db!sorteafilme` - Sorteia um filme para assistir.\n"
            "`db!removefilmeusuario <@usuário>` - Remove todos os filmes adicionados pelo usuário.\n"
            "`db!help` - Mostra esta mensagem de ajuda."
        )
        await ctx.send(help_message)
