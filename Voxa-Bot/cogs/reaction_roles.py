import discord
from discord.ext import commands
from discord.ui import View, Select

class RoleSelect(Select):
    def __init__(self, roles):
        options = [
            discord.SelectOption(label=role.name, value=str(role.id))
            for role in roles
        ]
        super().__init__(
            placeholder="Choose your roles...",
            min_values=0,
            max_values=len(options),
            options=options
        )
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        selected_role_ids = [int(v) for v in self.values]
        
        for role in self.roles:
            if role.id in selected_role_ids:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
                
        await interaction.response.send_message("Your roles have been updated!", ephemeral=True)

class RoleView(View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def droprole(self, ctx, *role_names):
        """
        Send a dropdown menu to let users pick roles.
        Example: !droprole admin member Wake up
        """
        if not role_names:
            await ctx.send("Please provide at least one role name.")
            return

        roles = []
        for name in role_names:
            role = discord.utils.get(ctx.guild.roles, name=name)
            if role:
                roles.append(role)

        if not roles:
            await ctx.send("No valid roles found. Make sure the names are correct.")
            return

        view = RoleView(roles)
        await ctx.send("Choose your roles:", view=view)

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
